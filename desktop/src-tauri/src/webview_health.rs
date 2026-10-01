//! WebView2 运行期健康：运行时版本探测 + 官方失败事件监听
//!
//! 对应微软官方方案里的两条：
//! 1. **运行时在不在、什么版本** —— 读 `pv`（REG_SZ），机器级与用户级各一处。
//!    官方原文见 Microsoft Learn *Distribute your app and the WebView2 Runtime*
//!    的 "Detect if a WebView2 Runtime is already installed"。
//! 2. **运行期进程崩了怎么办** —— 接官方事件 `CoreWebView2.ProcessFailed`
//!    （含"意外退出"与"无响应"两种条件）。没有它就只能靠超时猜，
//!    区分不出"渲染进程崩了"和"浏览器进程没了"。
//!
//! 这两件事都需要 Win32 / WebView2 COM，因此实现只放在 Windows 上；
//! 其他平台留空实现，保证这份 lib 仍能被移动端交叉编译复用。

/// 读取 WebView2 运行时版本；未安装（或值为空/0.0.0.0）返回 `None`
#[cfg(windows)]
pub fn runtime_version() -> Option<String> {
    /// 机器级（64 位系统在 WOW6432Node 下）
    const SUBKEY_MACHINE: &str =
        r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}";
    /// 用户级
    const SUBKEY_USER: &str =
        r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}";

    for (root, subkey) in [
        (ffi::HKEY_LOCAL_MACHINE, SUBKEY_MACHINE),
        (ffi::HKEY_CURRENT_USER, SUBKEY_USER),
    ] {
        if let Some(version) = ffi::read_pv(root, subkey) {
            let version = version.trim();
            if !version.is_empty() && version != "0.0.0.0" {
                return Some(version.to_string());
            }
        }
    }

    None
}

#[cfg(not(windows))]
pub fn runtime_version() -> Option<String> {
    None
}

/// 给主 WebView 挂上失败事件监听
///
/// 处置策略（简单、可预测）：
/// - **无响应**：官方文档说明该条件会每隔几秒重复上报直到恢复，因此只记一次日志，
///   既不重载也不退出（否则"界面卡一下"就会把应用杀掉）；
/// - **浏览器进程退出**：无法自愈 → 日志 + 中文原生弹窗 + 退出码 2；
/// - **其他进程崩溃**（渲染/GPU/工具）：记日志并尝试重载页面；
///   同一会话内超过 3 次即判定不可自愈，走同样的失败路径，
///   避免"崩溃—重载"无限循环把用户困在反复刷新的界面上。
#[cfg(windows)]
pub fn attach_failure_guard(app: &tauri::AppHandle) {
    use tauri::Manager;
    use webview2_com::ProcessFailedEventHandler;

    let Some(window) = app.get_webview_window(crate::WINDOW_LABEL) else {
        eprintln!("[webview] 找不到主窗口，跳过失败事件监听");
        return;
    };
    let app = app.clone();

    // 事件注册要在 UI 线程上执行；这里从后台线程发起，
    // 避免在 setup() 阶段同步等待事件循环而把自己锁死。
    std::thread::spawn(move || {
        let result = window.with_webview(move |webview| {
            let core = match unsafe { webview.controller().CoreWebView2() } {
                Ok(core) => core,
                Err(error) => {
                    eprintln!("[webview] 取 CoreWebView2 失败，跳过失败事件监听: {error}");
                    return;
                }
            };

            let mut token: i64 = 0;
            // 事件里要长期持有句柄，这里单独 clone 一份，避免把外层那个 move 走
            let app_for_handler = app.clone();
            let handler = ProcessFailedEventHandler::create(Box::new(move |_sender, args| {
                if let Some(args) = args {
                    use webview2_com::Microsoft::Web::WebView2::Win32::COREWEBVIEW2_PROCESS_FAILED_KIND_UNKNOWN_PROCESS_EXITED;

                    // 原始签名是 out-param：失败时退回兜底值，不影响后续判定
                    let mut kind = COREWEBVIEW2_PROCESS_FAILED_KIND_UNKNOWN_PROCESS_EXITED;
                    let _ = unsafe { args.ProcessFailedKind(&mut kind) };

                    on_process_failed(&app_for_handler, kind);
                }

                Ok(())
            }));

            match unsafe { core.add_ProcessFailed(&handler, &mut token) } {
                Ok(()) => {
                    crate::append_startup_log(&app, "已注册 WebView2 ProcessFailed 失败事件监听");
                }
                Err(error) => eprintln!("[webview] 注册 ProcessFailed 失败: {error}"),
            }
        });

        if let Err(error) = result {
            eprintln!("[webview] with_webview 调用失败: {error}");
        }
    });
}

#[cfg(not(windows))]
pub fn attach_failure_guard(_app: &tauri::AppHandle) {}

/// 失败事件的处置
///
/// 说明：`Reason` / `ExitCode` 定义在 `ICoreWebView2ProcessFailedEventArgs2` 上，
/// 取它们需要 `ICoreWebView2ProcessFailedEventArgs2::cast()`（即引入 `windows` crate 的
/// `Interface` trait）。为了不给工程再加一个直接依赖，这里只用 `ProcessFailedKind` ——
/// 它已经足以区分"浏览器进程没了 / 渲染进程崩了 / 无响应"这三类处置方式。
#[cfg(windows)]
fn on_process_failed(
    app: &tauri::AppHandle,
    kind: webview2_com::Microsoft::Web::WebView2::Win32::COREWEBVIEW2_PROCESS_FAILED_KIND,
) {
    use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
    use tauri::Manager;
    use webview2_com::Microsoft::Web::WebView2::Win32::{
        COREWEBVIEW2_PROCESS_FAILED_KIND_BROWSER_PROCESS_EXITED,
        COREWEBVIEW2_PROCESS_FAILED_KIND_RENDER_PROCESS_UNRESPONSIVE,
    };

    /// 单次运行内允许的自动恢复次数
    const MAX_AUTO_RECOVER: usize = 3;

    static FAILURES: AtomicUsize = AtomicUsize::new(0);
    static UNRESPONSIVE_LOGGED: AtomicBool = AtomicBool::new(false);

    if kind == COREWEBVIEW2_PROCESS_FAILED_KIND_RENDER_PROCESS_UNRESPONSIVE {
        if !UNRESPONSIVE_LOGGED.swap(true, Ordering::SeqCst) {
            let _ = crate::append_startup_log(
                app,
                "WebView2 渲染进程无响应（官方说明会每隔几秒重复上报，等待其自行恢复）",
            );
        }
        return;
    }

    let browser_gone = kind == COREWEBVIEW2_PROCESS_FAILED_KIND_BROWSER_PROCESS_EXITED;
    let attempt = FAILURES.fetch_add(1, Ordering::SeqCst) + 1;

    let _ = crate::append_startup_log(
        app,
        &format!(
            "WebView2 进程退出：kind={}（第 {} 次）",
            kind.0, attempt
        ),
    );

    if browser_gone || attempt > MAX_AUTO_RECOVER {
        let why = if browser_gone {
            "内嵌浏览器进程已退出"
        } else {
            "内嵌浏览器进程反复崩溃"
        };
        let log = crate::append_startup_log(app, &format!("{why}，判定不可自愈，应用退出"));
        crate::show_native_error(log.as_deref());
        std::process::exit(crate::EXIT_WEBVIEW_UNAVAILABLE);
    }

    // 渲染/GPU/工具进程崩：重载页面兜一次。
    // 不能在事件回调（UI 线程）里同步 eval —— 会自己等自己，所以另起线程。
    let app = app.clone();
    std::thread::spawn(move || {
        std::thread::sleep(std::time::Duration::from_millis(200));
        if let Some(window) = app.get_webview_window(crate::WINDOW_LABEL) {
            match window.eval("window.location.reload()") {
                Ok(()) => {
                    crate::append_startup_log(&app, "已尝试重载页面以从进程崩溃中恢复");
                }
                Err(error) => eprintln!("[webview] 重载页面失败: {error}"),
            }
        }
    });
}

// ─────────────────────────────────────────────
// Win32 注册表读取（只为读一个字符串，不引入 winreg 依赖）
// ─────────────────────────────────────────────

#[cfg(windows)]
mod ffi {
    use std::ffi::c_void;

    pub type Hkey = *mut c_void;

    /// 预定义注册表根键
    ///
    /// Windows 规定这几个"伪句柄"是 32 位常量做**符号扩展**后的值，
    /// 所以先转 i32 再转指针，保证 64 位下也是 0xFFFFFFFF8000_00xx。
    pub const HKEY_CURRENT_USER: Hkey = (0x8000_0001u32 as i32) as isize as Hkey;
    pub const HKEY_LOCAL_MACHINE: Hkey = (0x8000_0002u32 as i32) as isize as Hkey;

    /// 只接受 REG_SZ（避免把别的类型当字符串读）
    const RRF_RT_REG_SZ: u32 = 0x0000_0002;

    #[link(name = "advapi32")]
    extern "system" {
        fn RegGetValueW(
            hkey: Hkey,
            subkey: *const u16,
            value: *const u16,
            flags: u32,
            value_type: *mut u32,
            data: *mut c_void,
            data_size: *mut u32,
        ) -> i32;
    }

    fn wide(text: &str) -> Vec<u16> {
        text.encode_utf16().chain(std::iter::once(0)).collect()
    }

    /// 读取指定注册表位置下的 `pv` 字符串值
    pub fn read_pv(root: Hkey, subkey: &str) -> Option<String> {
        let subkey = wide(subkey);
        let value = wide("pv");

        let mut buffer = [0u16; 64];
        let mut size = (buffer.len() * std::mem::size_of::<u16>()) as u32;
        let mut value_type = 0u32;

        // SAFETY: 三个指针都指向本次调用期间存活的缓冲区，size 与 buffer 容量一致。
        let code = unsafe {
            RegGetValueW(
                root,
                subkey.as_ptr(),
                value.as_ptr(),
                RRF_RT_REG_SZ,
                &mut value_type,
                buffer.as_mut_ptr() as *mut c_void,
                &mut size,
            )
        };

        if code != 0 {
            return None;
        }

        // RegGetValueW 返回的 size 含结尾 NUL，这里减掉
        let chars = (size as usize / std::mem::size_of::<u16>()).saturating_sub(1);
        Some(String::from_utf16_lossy(&buffer[..chars.min(buffer.len())]))
    }
}
