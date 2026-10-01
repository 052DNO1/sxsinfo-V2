//! LIMS 桌面端外壳
//!
//! 职责边界：本工程只做「壳」，不含任何业务代码。
//! - 承载前端构建产物（`../web`，由使用者从 `frontend/dist/pc` 原样复制）
//! - 在页面脚本执行前注入桌面端配置（`window.__LIMS_CONFIG__`）
//! - 提供服务器地址的读写命令，配置落在系统应用配置目录
//! - 单实例、窗口状态持久化、原生窗口行为

mod app_config;
mod desktop_chrome;
mod menu;
mod single_instance;
mod webview_health;
mod webview_shell;
mod window_state;

use std::error::Error;
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::mpsc::Receiver;
use std::sync::Arc;
use std::time::Duration;

use tauri::{AppHandle, Manager, WebviewUrl, WebviewWindow, WebviewWindowBuilder};

use app_config::AppConfig;
use single_instance::AcquireResult;

/// 主窗口标签：capabilities、窗口状态、单实例唤醒都按它定位
pub const WINDOW_LABEL: &str = "main";

/// 应用入口页
///
/// 前端 PC 端产物是 `index.pc.html`（不是默认的 index.html），
/// 这里显式指定，避免为了迁就框架去改名而破坏「构建产物原样复制」的原则。
const ENTRY_PAGE: &str = "index.pc.html";

const WINDOW_TITLE: &str = "实训室信息管理系统";

/// WebView2 未就绪的等待上限（毫秒），可用环境变量 `LIMS_WEBVIEW_TIMEOUT_MS` 覆盖
///
/// 取值偏大是有意的：正常机器上 WebView2 环境创建通常不到 2 秒，
/// 但首次运行（用户数据目录为空）或机械硬盘上可能到十几秒。
/// 这里只在「明显不正常」时才判定失败，避免把「慢」当成「坏」。
const DEFAULT_WEBVIEW_TIMEOUT_MS: u64 = 30_000;

/// 看门狗判定启动失败时的进程退出码
/// （便于脚本/运维区分「WebView 起不来」与「用户正常关闭」）
pub(crate) const EXIT_WEBVIEW_UNAVAILABLE: i32 = 2;

/// 启动日志文件名（与 WebView2 数据同目录，便于一次性打包取证）
const STARTUP_LOG_FILE: &str = "startup.log";

/// 启动日志体积上限，超过即整体重写，避免长期运行把磁盘写满
const STARTUP_LOG_MAX_BYTES: u64 = 512 * 1024;

/// 便携模式下 WebView2 数据目录名（放在 exe 同级）
const PORTABLE_DATA_DIR: &str = "lims-webview2-data";

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // 单实例判定必须发生在创建窗口之前
    let activation: Option<Receiver<()>> = match single_instance::acquire() {
        AcquireResult::Primary(receiver) => Some(receiver),
        // 已有实例在运行：handshake 阶段已请求它激活窗口，本进程直接退出
        AcquireResult::Secondary => return,
        // 无法判定（端口被无关程序占用）：放弃单实例保护，保证应用照常可用
        AcquireResult::Unavailable => None,
    };

    tauri::Builder::default()
        .setup(move |app| {
            let config = AppConfig::load(app.handle());
            let window = build_main_window(app, &config)?;

            // 菜单：自绘外壳时由应用内标题栏承载，不再挂原生菜单条
            if desktop_chrome::CUSTOM_CHROME {
                append_startup_log(&app.handle().clone(), "自绘外壳模式：原生菜单栏已交由应用内菜单接管");
            } else {
                // 菜单失败不致命：只记录日志，绝不因此让应用起不来
                match menu::build(app.handle()) {
                    Ok(app_menu) => {
                        if let Err(error) = app.set_menu(app_menu) {
                            eprintln!("[menu] 设置菜单栏失败，已跳过: {error}");
                        }
                    }
                    Err(error) => eprintln!("[menu] 构建菜单栏失败，已跳过: {error}"),
                }
            }

            if let Some(receiver) = activation {
                spawn_activation_listener(window, receiver);
            }

            Ok(())
        })
        .on_menu_event(|app, event| {
            menu::handle_event(app, event.id().as_ref());
        })
        .on_window_event(|window, event| {
            if window.label() != WINDOW_LABEL {
                return;
            }

            match event {
                tauri::WindowEvent::Resized(_) | tauri::WindowEvent::Moved(_) => {
                    window_state::capture(window);
                    // 最大化/还原时让自绘标题栏的按钮图标跟着变
                    if let Some(webview) = window.app_handle().get_webview_window(WINDOW_LABEL) {
                        desktop_chrome::emit_window_state(&webview);
                    }
                }
                tauri::WindowEvent::ThemeChanged(_) => {
                    if let Some(webview) = window.app_handle().get_webview_window(WINDOW_LABEL) {
                        let theme = desktop_chrome::theme_name(&webview);
                        desktop_chrome::emit_theme(&webview, theme);
                    }
                }
                tauri::WindowEvent::CloseRequested { .. } | tauri::WindowEvent::Destroyed => {
                    window_state::capture(window);
                    window_state::persist(window.app_handle());
                }
                _ => {}
            }
        })
        .invoke_handler(tauri::generate_handler![
            app_config::get_server_config,
            app_config::set_server_config,
            desktop_chrome::shell_window,
            desktop_chrome::shell_menu,
            desktop_chrome::shell_sync
        ])
        .run(tauri::generate_context!())
        .expect("桌面应用启动失败");
}

/// 创建主窗口，并把配置作为初始化脚本注入
fn build_main_window(
    app: &mut tauri::App,
    config: &AppConfig,
) -> Result<WebviewWindow, Box<dyn Error>> {
    let handle = app.handle().clone();
    let state = window_state::load(&handle);
    let script = config.initialization_script();

    // 必须在创建窗口前把 WebView2 的数据目录准备好，否则可能启动即崩溃。
    // 详见 prepare_webview_data_dir 的说明。
    let data_dir = prepare_webview_data_dir(&handle);

    append_startup_log(
        &handle,
        &format!(
            "启动 identifier={} WebView2数据目录={}",
            app.config().identifier,
            data_dir
                .as_deref()
                .map(|path| path.display().to_string())
                .unwrap_or_else(|| "（准备失败，交由 WebView2 自行处理）".to_string())
        ),
    );

    // 看门狗必须早于 build() 布置：WebView2 异常时 build() 可能永远不返回
    let ready = Arc::new(AtomicBool::new(false));
    spawn_webview_watchdog(handle.clone(), Arc::clone(&ready));

    let mut builder = WebviewWindowBuilder::new(app, WINDOW_LABEL, WebviewUrl::App(ENTRY_PAGE.into()))
        .title(WINDOW_TITLE)
        .inner_size(state.width, state.height)
        .min_inner_size(window_state::MIN_WIDTH, window_state::MIN_HEIGHT)
        .resizable(true)
        // 自绘外壳：去掉系统标题栏，由前端 TitleBar 承载（标题仍用于任务栏/Alt-Tab）
        .decorations(!desktop_chrome::CUSTOM_CHROME)
        .center()
        // 该脚本先于页面内所有脚本执行，前端可同步读到配置
        .initialization_script(script.as_str());

    if let Some(dir) = data_dir {
        builder = builder.data_directory(dir);
    }

    // 只在保存过位置时恢复，否则交给 center()
    if let (Some(x), Some(y)) = (state.x, state.y) {
        builder = builder.position(x, y);
    }

    let window = match builder.build() {
        Ok(window) => window,
        Err(error) => {
            // 既然已经明确失败，就不必再等看门狗判定。
            // 给出与看门狗一致的提示后主动退出，而不是让 Tauri 打出
            // "Failed to setup app" 的 panic —— 那句话对现场人员毫无信息量。
            ready.store(true, Ordering::SeqCst);
            eprintln!("[webview] 创建窗口/WebView 失败: {error}");
            let log = append_startup_log(&handle, &format!("创建窗口/WebView 失败: {error}"));
            show_native_error(log.as_deref());
            std::process::exit(EXIT_WEBVIEW_UNAVAILABLE);
        }
    };

    ready.store(true, Ordering::SeqCst);

    // 记录运行时版本：出问题时这一行能立刻回答"机器上到底装没装、哪个版本"
    let _ = match webview_health::runtime_version() {
        Some(version) => append_startup_log(&handle, &format!("WebView2 运行时版本 {version}")),
        None => append_startup_log(&handle, "未检测到 WebView2 运行时（pv 注册表缺失）"),
    };
    append_startup_log(&handle, "WebView 已就绪，开始加载前端资源");

    // 运行期失败监听：官方 ProcessFailed / BrowserProcessExited
    webview_health::attach_failure_guard(&handle);

    // 应用化策略：关掉浏览器行为（右键菜单/状态栏/缩放/快捷键/弹窗/外部导航）
    webview_shell::apply(&handle);

    if state.maximized {
        let _ = window.maximize();
    }

    // 外壳修饰：
    // - 自绘外壳 → Win11 圆角 + 描边（否则无边框窗口是直角方块）
    // - 系统标题栏 → 刷成品牌色，至少别是系统默认灰
    if desktop_chrome::CUSTOM_CHROME {
        desktop_chrome::apply_window_chrome(&window);
    } else {
        webview_shell::paint_title_bar(&window);
    }

    Ok(window)
}

/// 监听后续实例的激活请求，把窗口重新显示到前台
fn spawn_activation_listener(window: WebviewWindow, receiver: Receiver<()>) {
    std::thread::spawn(move || {
        while receiver.recv().is_ok() {
            let _ = window.show();
            let _ = window.unminimize();
            let _ = window.set_focus();
        }
    });
}

/// 准备 WebView2 的用户数据目录，返回其路径
///
/// 【为什么必须由我们自己建】
/// WebView2 在无法自行创建该目录时，不会给出可读的错误，而是直接以
/// `os error 5`（拒绝访问）让窗口创建失败 —— 表现就是**应用启动即崩溃，
/// 用户看不到任何提示**。实测：目录不存在时启动必崩，目录已存在时启动正常。
/// 因此这里先替它把目录建出来，把这个失败模式从根上消掉。
///
/// 【为什么还要"试写"而不只是"建目录"（2026-09-30 补）】
/// 目录**已存在**时 `create_dir_all` 会直接返回成功，**哪怕当前进程对它没有
/// 写权限**。一旦把这种目录交给 WebView2，浏览器进程会在早期初始化时崩溃
/// （实测：`msedge_elf.dll`、异常码 `0x80000003`），表现就是白窗口 —— 而且
/// 这种"坏目录"会一直躺在磁盘上，让之后**每一次**启动都继续崩。
/// 所以这里必须真写一个探针文件，确认可写才采用；否则换下一个候选位置。
///
/// 【候选顺序】
/// 1. 应用数据目录（`%LOCALAPPDATA%\<identifier>\WebView2`）—— 正常运行时的位置
/// 2. **可执行文件所在目录**（`<exe目录>\lims-webview2-data`）—— 便携部署用；
///    更重要的是：当进程被文件级限制（例如从沙箱化的工作区界面里启动）时，
///    应用数据目录与临时目录**都**写不进去，而 exe 所在目录往往是唯一可写的位置。
///    没有这一级时，那种启动方式下 WebView2 必然起不来（白屏）。
/// 3. 系统临时目录 —— 最后的兜底
///
/// 返回 `None` 表示三处都不可写，此时不设置 `data_directory`，
/// 交回 WebView2 自行处理，避免把"我们准备失败"变成"应用完全起不来"。
fn prepare_webview_data_dir(app: &AppHandle) -> Option<PathBuf> {
    for dir in webview_data_dir_candidates(app) {
        match ensure_writable_dir(&dir) {
            Ok(()) => return Some(dir),
            Err(error) => eprintln!(
                "[webview] 用户数据目录 {} 不可用，尝试下一个: {error}",
                dir.display()
            ),
        }
    }

    eprintln!("[webview] 没有可写的用户数据目录，交由 WebView2 自行处理");
    None
}

/// WebView2 用户数据目录的候选位置（按优先级）
fn webview_data_dir_candidates(app: &AppHandle) -> Vec<PathBuf> {
    let mut candidates: Vec<PathBuf> = Vec::new();

    if let Ok(dir) = app.path().app_local_data_dir() {
        candidates.push(dir.join("WebView2"));
    }
    if let Some(dir) = executable_dir() {
        candidates.push(dir.join(PORTABLE_DATA_DIR));
    }
    candidates.push(std::env::temp_dir().join("lims-desktop-webview2"));

    candidates
}

/// 当前可执行文件所在目录
fn executable_dir() -> Option<PathBuf> {
    std::env::current_exe()
        .ok()?
        .parent()
        .map(Path::to_path_buf)
}

/// 建目录并试写一个探针文件，确认它**真的可写**
///
/// 只做 `create_dir_all` 是不够的：目录存在即返回成功，
/// 权限不对时会把一个不可写的目录当成可用目录交给 WebView2。
fn ensure_writable_dir(dir: &Path) -> Result<(), std::io::Error> {
    fs::create_dir_all(dir)?;

    let probe = dir.join(".write-probe");
    fs::write(&probe, b"ok")?;
    let _ = fs::remove_file(&probe);

    Ok(())
}

// ─────────────────────────────────────────────
// 启动自检：WebView2 起不来时，给出可读的失败
// ─────────────────────────────────────────────

/// 读取看门狗超时时间
fn webview_timeout() -> Duration {
    let ms = std::env::var("LIMS_WEBVIEW_TIMEOUT_MS")
        .ok()
        .and_then(|value| value.trim().parse::<u64>().ok())
        .filter(|ms| *ms >= 3_000)
        .unwrap_or(DEFAULT_WEBVIEW_TIMEOUT_MS);

    Duration::from_millis(ms)
}

/// 后台盯着「WebView 是否就绪」，超时即判定启动失败
///
/// 【为什么需要】
/// WebView2 的浏览器进程一旦启动失败，`WebviewWindowBuilder::build()`
/// 会**永远不返回**：不报错、不退出。用户看到的是白窗口，或者
/// 「双击了没反应」；而进程还占着单实例端口，后续双击都会静默退出，
/// 现场完全无从下手。实测触发条件之一：WebView2 运行时自身崩溃
/// （`msedge_elf.dll`、异常码 0x80000003），此时连一个 `msedgewebview2.exe`
/// 子进程都留不下来，只有 Windows 应用程序日志里才有痕迹。
///
/// 这个线程负责兜底：超时仍未就绪 → 写启动日志 + 弹原生对话框 + 退出。
fn spawn_webview_watchdog(app: AppHandle, ready: Arc<AtomicBool>) {
    let timeout = webview_timeout();

    std::thread::spawn(move || {
        let step = Duration::from_millis(500);
        let mut waited = Duration::ZERO;

        while waited < timeout {
            if ready.load(Ordering::SeqCst) {
                return;
            }
            std::thread::sleep(step);
            waited += step;
        }

        // 睡眠期间可能刚好就绪，这里必须再确认一次，避免误杀慢启动
        if ready.load(Ordering::SeqCst) {
            return;
        }

        eprintln!("[webview] {} 秒内未就绪，判定启动失败", timeout.as_secs());
        let log = append_startup_log(
            &app,
            &format!(
                "WebView2 在 {} 秒内未就绪，判定为浏览器组件异常，应用以退出码 {EXIT_WEBVIEW_UNAVAILABLE} 退出",
                timeout.as_secs()
            ),
        );
        show_native_error(log.as_deref());
        std::process::exit(EXIT_WEBVIEW_UNAVAILABLE);
    });
}

/// 启动日志的候选位置（按优先级）
///
/// 1. 应用数据目录
/// 2. **可执行文件所在目录** —— 进程被文件级限制时，这里通常还能写，
///    日志因此仍有落点（现场排查靠它，不然"没有日志"就真的什么都没有）
/// 3. 系统临时目录
fn startup_log_candidates(app: &AppHandle) -> Vec<PathBuf> {
    let mut candidates = Vec::new();

    if let Ok(dir) = app.path().app_local_data_dir() {
        candidates.push(dir.join(STARTUP_LOG_FILE));
    }
    if let Some(dir) = executable_dir() {
        candidates.push(dir.join(STARTUP_LOG_FILE));
    }
    candidates.push(std::env::temp_dir().join(STARTUP_LOG_FILE));

    candidates
}

/// 追加一行启动日志，返回**实际写入成功**的文件路径
///
/// best-effort：写入失败只记 stderr，绝不允许影响应用启动。
pub(crate) fn append_startup_log(app: &AppHandle, message: &str) -> Option<PathBuf> {
    let seconds = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|elapsed| elapsed.as_secs())
        .unwrap_or(0);
    let line = format!("[unix {seconds}] {message}\n");

    for path in startup_log_candidates(app) {
        if let Some(parent) = path.parent() {
            let _ = fs::create_dir_all(parent);
        }

        // 体积保护：超过上限就整体重写，宁可丢掉很久以前的记录
        if let Ok(meta) = fs::metadata(&path) {
            if meta.len() > STARTUP_LOG_MAX_BYTES {
                let _ = fs::remove_file(&path);
            }
        }

        let result = fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&path)
            .and_then(|mut file| file.write_all(line.as_bytes()));

        match result {
            Ok(()) => return Some(path),
            Err(error) => eprintln!("[log] 写入 {} 失败: {error}", path.display()),
        }
    }

    eprintln!("[log] 所有候选位置都无法写入启动日志");
    None
}

/// 弹出原生错误对话框，并把日志路径一并告知
///
/// 刻意不依赖插件或前端：走到这里时界面根本起不来，
/// 唯一还能用的通道就是 Win32 的 MessageBox。
pub(crate) fn show_native_error(log: Option<&Path>) {
    let mut text = String::from(
        "桌面端无法初始化内嵌浏览器组件（WebView2），界面因此无法显示。\n\n\
         这通常是本机 Microsoft Edge WebView2 运行时损坏或异常导致的，\
         与应用自身的数据无关。请依次尝试：\n\
         1. 重启电脑；\n\
         2. 修复或重新安装「Microsoft Edge WebView2 运行时」（微软官方 Evergreen 安装包）；\n\
         3. 若仍无效，请把下面的日志文件一并反馈给运维；\n\
         4. 进一步排查：在「事件查看器 → Windows 日志 → 应用程序」中\n\
            查找 msedgewebview2.exe 的错误记录，连同日志一起反馈。",
    );

    // 把"运行时到底在不在、什么版本"直接写进提示里：
    // 现场看到"未检测到运行时"就知道该去装运行时，而不是去查数据目录
    match webview_health::runtime_version() {
        Some(version) => {
            text.push_str("\n\n检测到的 WebView2 运行时：");
            text.push_str(&version);
        }
        None => {
            text.push_str(
                "\n\n检测到的 WebView2 运行时：未安装（注册表里没有 pv 记录）。\n\
                 请先安装「Microsoft Edge WebView2 运行时」再启动本应用。",
            );
        }
    }

    if let Some(path) = log {
        text.push_str("\n\n日志文件：\n");
        text.push_str(&path.display().to_string());
    } else {
        text.push_str("\n\n（启动日志写入失败，可能被本机安全策略拦截，请直接反馈以上内容。）");
    }

    message_box("实训室信息管理系统 - 启动失败", &text, 0x0000_0010);
}

/// 弹出信息框（用于「帮助 → 关于」这类正常提示）
pub(crate) fn show_info(title: &str, text: &str) {
    // MB_ICONINFORMATION = 0x40（非 Windows 平台该参数被忽略）
    message_box(title, text, 0x0000_0040);
}

#[cfg(windows)]
fn message_box(title: &str, text: &str, icon: u32) {
    const MB_OK: u32 = 0x0000_0000;
    const MB_SETFOREGROUND: u32 = 0x0001_0000;
    const MB_TOPMOST: u32 = 0x0004_0000;

    let text: Vec<u16> = text.encode_utf16().chain(std::iter::once(0)).collect();
    let title: Vec<u16> = title.encode_utf16().chain(std::iter::once(0)).collect();

    // SAFETY: 两个指针都指向以 NUL 结尾、且在调用期间始终存活的 UTF-16 缓冲；
    // MessageBoxW 是阻塞调用，返回之后这两个缓冲才会被释放。
    unsafe {
        let _ = MessageBoxW(
            std::ptr::null_mut(),
            text.as_ptr(),
            title.as_ptr(),
            MB_OK | icon | MB_SETFOREGROUND | MB_TOPMOST,
        );
    }
}

#[cfg(not(windows))]
fn message_box(_title: &str, _text: &str, _icon: u32) {
    // 非 Windows 平台不弹窗，原因已经写进启动日志
}

// 直接声明 Win32 的 `MessageBoxW`
//
// 刻意不为一个对话框引入 windows-sys / winapi：
// 本工程的原则是「依赖越少，构建越不依赖网络，攻击面越小」。
#[cfg(windows)]
#[link(name = "user32")]
extern "system" {
    fn MessageBoxW(
        hwnd: *mut core::ffi::c_void,
        text: *const u16,
        caption: *const u16,
        utype: u32,
    ) -> i32;
}
