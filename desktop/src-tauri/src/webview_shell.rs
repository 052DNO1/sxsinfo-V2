//! 桌面外壳的「应用感」策略：把 WebView 的浏览器行为收紧成原生应用的样子
//!
//! 【为什么需要】
//! 内核是 WebView2，默认带着一堆浏览器行为。用户一眼看出"这是浏览器套壳"的，
//! 往往不是界面本身，而是这些细节：右键弹出"刷新/检查/另存为"、悬停显示目标网址的状态栏、
//! Ctrl+P 打印框、Ctrl+F 查找条、Ctrl+滚轮缩放、密码/表单自动填充气泡、
//! 拖文件进窗口直接跳走、`target=_blank` 弹新窗口、连不上时显示 Chromium 的"无法访问此页面"。
//!
//! 这里逐条按 WebView2 官方 API 关掉：
//!
//! | 浏览器行为 | 处理方式 |
//! | --- | --- |
//! | 默认右键菜单 | `AreDefaultContextMenusEnabled = false` |
//! | 悬停显示 URL 的状态栏 | `IsStatusBarEnabled = false` |
//! | 缩放界面（Ctrl+滚轮 / 手势） | `IsZoomControlEnabled = false`、`IsPinchZoomEnabled = false` |
//! | Chromium 自带错误页 | `IsBuiltInErrorPageEnabled = false` |
//! | 宿主对象注入面 | `AreHostObjectsAllowed = false` |
//! | 密码保存 / 表单自动填充气泡 | `IsPasswordAutosaveEnabled = false`、`IsGeneralAutofillEnabled = false` |
//! | 触摸板左右滑返回 | `IsSwipeNavigationEnabled = false` |
//! | F5 / Ctrl+P / Ctrl+F / F12 等浏览器快捷键 | `AreBrowserAcceleratorKeysEnabled = false` |
//! | `window.open` / `target=_blank` 弹窗 | `NewWindowRequested` 里取消 |
//! | 外部链接、拖入文件导致窗口跳走 | `NavigationStarting` 只放行应用自身来源，其余交给系统浏览器 |
//! | 启动白闪 | 控制器默认背景色刷成应用底色 |
//! | 任务栏身份（固定到任务栏后各自成组） | 显式设置 AppUserModelID |
//! | 系统默认灰标题栏 | DWM 标题栏刷成品牌蓝 + 白字（Win11 22H2+） |
//!
//! 【有意不关的】
//! - **开发者工具**：现场排错要用（见 `menu.rs` 的说明）。只关掉 F12 这类键盘快捷键，
//!   「视图 → 开发者工具」菜单项仍然可用；
//! - **脚本对话框**（`alert`/`confirm`）：前端确实在用（如空闲超时提示）；
//! - **文本选择**：这是数据类应用的刚需（表格里要能选、能复制）。
//!
//! 【为什么需要 windows crate】
//! 上面这些属性大多在 WebView2 的**版本化接口**上（`ICoreWebView2Controller2`、
//! `ICoreWebView2Settings3`~`6`），拿到它们要用 `Interface::cast`。
//! 它与 webview2-com 用的是同一套 windows-rs（已在 Cargo.lock 与本地缓存里），不新增依赖下载。

use tauri::AppHandle;

/// 应用品牌色（与前端登录页/加载页一致：#1890FF 蓝、#F0F2F5 灰底）
#[cfg(windows)]
const BRAND_BLUE_COLORREF: u32 = 0x00FF_9018; // COLORREF = 0x00BBGGRR
#[cfg(windows)]
const BRAND_WHITE_COLORREF: u32 = 0x00FF_FFFF;
#[cfg(windows)]
const APP_BACKGROUND: (u8, u8, u8) = (240, 242, 245);

/// 应用自身的来源：只有它才允许在窗口内导航
#[cfg(windows)]
const APP_ORIGINS: [&str; 3] = [
    "http://tauri.localhost",
    "https://tauri.localhost",
    "tauri://localhost",
];

#[cfg(windows)]
pub fn apply(app: &AppHandle) {
    use tauri::Manager;

    // 任务栏身份只需要设置一次，与 WebView 无关
    set_app_user_model_id();

    let Some(window) = app.get_webview_window(crate::WINDOW_LABEL) else {
        eprintln!("[shell] 找不到主窗口，跳过应用化策略");
        return;
    };
    let app = app.clone();

    // 与失败监听一样从后台线程发起，避免在 setup() 里同步等待事件循环
    std::thread::spawn(move || {
        let result = window.with_webview(move |webview| {
            let controller = webview.controller();

            let core = match unsafe { controller.CoreWebView2() } {
                Ok(core) => core,
                Err(error) => {
                    eprintln!("[shell] 取 CoreWebView2 失败，跳过应用化策略: {error}");
                    return;
                }
            };

            apply_background(&controller);
            apply_settings(&controller, &app);
            register_events(&core, &app);
        });

        if let Err(error) = result {
            eprintln!("[shell] with_webview 调用失败: {error}");
        }
    });
}

#[cfg(not(windows))]
pub fn apply(_app: &AppHandle) {}

/// 启动时不再白闪：把控制器默认背景色刷成与前端加载页同色
///
/// `SetDefaultBackgroundColor` 在 `ICoreWebView2Controller2` 上，需要 cast。
#[cfg(windows)]
fn apply_background(
    controller: &webview2_com::Microsoft::Web::WebView2::Win32::ICoreWebView2Controller,
) {
    use windows::core::Interface;
    use webview2_com::Microsoft::Web::WebView2::Win32::{
        ICoreWebView2Controller2, COREWEBVIEW2_COLOR,
    };

    let Ok(controller2) = controller.cast::<ICoreWebView2Controller2>() else {
        return; // 旧运行时没有该接口：白闪是外观问题，不值得报错
    };

    let _ = unsafe {
        controller2.SetDefaultBackgroundColor(COREWEBVIEW2_COLOR {
            A: 255,
            R: APP_BACKGROUND.0,
            G: APP_BACKGROUND.1,
            B: APP_BACKGROUND.2,
        })
    };
}

/// 收紧 WebView2 设置，并把每一项的返回结果写进启动日志
///
/// 这里记录的是 **setter 的返回码** 而不是读回属性：读回要 `windows_core::BOOL` 这套类型，
/// 收益有限；而 setter 返回错误才是真正需要被发现的情况（例如运行时太旧不支持某个属性）。
/// 策略是否真的生效，靠行为验证（右键是否弹菜单、外链是否被转交）而不是自报。
#[cfg(windows)]
fn apply_settings(
    controller: &webview2_com::Microsoft::Web::WebView2::Win32::ICoreWebView2Controller,
    app: &AppHandle,
) {
    use windows::core::Interface;
    use webview2_com::Microsoft::Web::WebView2::Win32::{
        ICoreWebView2Settings3, ICoreWebView2Settings4, ICoreWebView2Settings5,
        ICoreWebView2Settings6,
    };

    let core = match unsafe { controller.CoreWebView2() } {
        Ok(core) => core,
        Err(error) => {
            eprintln!("[shell] 取 CoreWebView2 失败: {error}");
            return;
        }
    };
    let settings = match unsafe { core.Settings() } {
        Ok(settings) => settings,
        Err(error) => {
            eprintln!("[shell] 取 Settings 失败: {error}");
            return;
        }
    };

    let mut failed: Vec<&'static str> = Vec::new();

    // 基础设置（ICoreWebView2Settings）
    // SAFETY: 均为设置布尔属性
    unsafe {
        if settings.SetAreDefaultContextMenusEnabled(false).is_err() {
            failed.push("默认右键菜单");
        }
        if settings.SetIsStatusBarEnabled(false).is_err() {
            failed.push("状态栏");
        }
        if settings.SetIsZoomControlEnabled(false).is_err() {
            failed.push("缩放");
        }
        if settings.SetIsBuiltInErrorPageEnabled(false).is_err() {
            failed.push("内置错误页");
        }
        if settings.SetAreHostObjectsAllowed(false).is_err() {
            failed.push("宿主对象");
        }
        if settings.SetAreDevToolsEnabled(true).is_err() {
            failed.push("开发者工具");
        }
        if settings.SetAreDefaultScriptDialogsEnabled(true).is_err() {
            failed.push("脚本对话框");
        }
    }

    // 版本化设置：接口不存在（运行时偏旧）时记一笔，但不影响其余策略
    let accelerator_keys = match settings.cast::<ICoreWebView2Settings3>() {
        Ok(settings3) => unsafe { settings3.SetAreBrowserAcceleratorKeysEnabled(false) }.is_ok(),
        Err(_) => false,
    };

    let autofill = match settings.cast::<ICoreWebView2Settings4>() {
        Ok(settings4) => unsafe {
            settings4.SetIsPasswordAutosaveEnabled(false).is_ok()
                && settings4.SetIsGeneralAutofillEnabled(false).is_ok()
        },
        Err(_) => false,
    };

    // 注意接口归属：IsPinchZoomEnabled 在 Settings5，IsSwipeNavigationEnabled 在 Settings6
    let pinch_zoom = match settings.cast::<ICoreWebView2Settings5>() {
        Ok(settings5) => unsafe { settings5.SetIsPinchZoomEnabled(false) }.is_ok(),
        Err(_) => false,
    };
    let swipe_nav = match settings.cast::<ICoreWebView2Settings6>() {
        Ok(settings6) => unsafe { settings6.SetIsSwipeNavigationEnabled(false) }.is_ok(),
        Err(_) => false,
    };

    let failed_text = if failed.is_empty() {
        "全部成功".to_string()
    } else {
        format!("失败项：{}", failed.join("、"))
    };

    crate::append_startup_log(
        app,
        &format!(
            "应用化策略：{}；浏览器快捷键={} 自动填充={} 双指缩放={} 滑动返回={}",
            failed_text,
            yes_no(accelerator_keys),
            yes_no(autofill),
            yes_no(pinch_zoom),
            yes_no(swipe_nav)
        ),
    );
}

#[cfg(windows)]
fn yes_no(applied: bool) -> &'static str {
    if applied {
        "已关"
    } else {
        "未支持"
    }
}

/// 注册两类事件：弹窗取消、导航白名单
#[cfg(windows)]
fn register_events(
    core: &webview2_com::Microsoft::Web::WebView2::Win32::ICoreWebView2,
    app: &AppHandle,
) {
    use webview2_com::{NavigationStartingEventHandler, NewWindowRequestedEventHandler};

    // 1) window.open / target=_blank：直接取消，不让它冒出新窗口
    let mut token_new_window: i64 = 0;
    let app_for_window = app.clone();
    let handler = NewWindowRequestedEventHandler::create(Box::new(move |_sender, args| {
        if let Some(args) = args {
            let _ = unsafe { args.SetHandled(true) };
            let _ =
                crate::append_startup_log(&app_for_window, "已拦截一次新窗口请求（window.open）");
        }
        Ok(())
    }));
    if let Err(error) = unsafe { core.add_NewWindowRequested(&handler, &mut token_new_window) } {
        eprintln!("[shell] 注册新窗口拦截失败: {error}");
    }

    // 2) 导航白名单：只允许应用自身来源；外部链接交给系统默认浏览器
    let mut token_nav: i64 = 0;
    let app_for_nav = app.clone();
    let handler = NavigationStartingEventHandler::create(Box::new(move |_sender, args| {
        let Some(args) = args else { return Ok(()) };

        let mut raw = webview2_com::pwstr_from_str("");
        if unsafe { args.Uri(&mut raw) }.is_err() {
            return Ok(());
        }
        let uri = webview2_com::take_pwstr(raw);

        if uri.is_empty() || uri == "about:blank" || uri.starts_with("data:") {
            return Ok(());
        }
        if APP_ORIGINS.iter().any(|origin| uri.starts_with(origin)) {
            return Ok(());
        }

        // 应用外的一律不放行：取消导航 + 交给系统浏览器（拖入文件、外链点击都会走到这里）
        let _ = unsafe { args.SetCancel(true) };
        let _ = crate::append_startup_log(
            &app_for_nav,
            &format!("已拦截窗口内导航并转交系统浏览器：{uri}"),
        );
        ffi::open_in_system_browser(&uri);

        Ok(())
    }));
    if let Err(error) = unsafe { core.add_NavigationStarting(&handler, &mut token_nav) } {
        eprintln!("[shell] 注册导航白名单失败: {error}");
    }

    let _ = crate::append_startup_log(app, "应用化策略已注册：新窗口拦截 / 导航白名单");
}

// ─────────────────────────────────────────────
// Win32 辅助：任务栏身份、标题栏配色、外部浏览器
// ─────────────────────────────────────────────

#[cfg(windows)]
fn set_app_user_model_id() {
    let id = ffi::wide("com.sxsinfo.lims.desktop");
    // SAFETY: 传入以 NUL 结尾的宽字符串
    let _ = unsafe { ffi::SetCurrentProcessExplicitAppUserModelID(id.as_ptr()) };
}

/// 把标题栏刷成品牌色（仅 Win11 22H2+ 支持；不支持时静默跳过）
#[cfg(windows)]
pub fn paint_title_bar(window: &tauri::WebviewWindow) {
    let Ok(handle) = window.hwnd() else { return };
    let hwnd = handle.0 as *mut std::ffi::c_void;

    // DWMWA_CAPTION_COLOR = 35, DWMWA_TEXT_COLOR = 36
    for (attribute, color) in [(35u32, BRAND_BLUE_COLORREF), (36u32, BRAND_WHITE_COLORREF)] {
        let value = color;
        // SAFETY: 属性值与文档要求的 DWORD 大小一致
        let _ = unsafe {
            ffi::DwmSetWindowAttribute(
                hwnd,
                attribute,
                &value as *const u32 as *const std::ffi::c_void,
                std::mem::size_of::<u32>() as u32,
            )
        };
    }
}

#[cfg(not(windows))]
pub fn paint_title_bar(_window: &tauri::WebviewWindow) {}

#[cfg(windows)]
mod ffi {
    use std::ffi::c_void;

    #[link(name = "shell32")]
    extern "system" {
        pub fn SetCurrentProcessExplicitAppUserModelID(app_id: *const u16) -> i32;
        pub fn ShellExecuteW(
            hwnd: *mut c_void,
            operation: *const u16,
            file: *const u16,
            parameters: *const u16,
            directory: *const u16,
            show_cmd: i32,
        ) -> *mut c_void;
    }

    #[link(name = "dwmapi")]
    extern "system" {
        pub fn DwmSetWindowAttribute(
            hwnd: *mut c_void,
            attribute: u32,
            value: *const c_void,
            size: u32,
        ) -> i32;
    }

    pub fn wide(text: &str) -> Vec<u16> {
        text.encode_utf16().chain(std::iter::once(0)).collect()
    }

    /// 用系统默认浏览器打开链接（应用内不放行外部导航时的落点）
    pub fn open_in_system_browser(url: &str) {
        let operation = wide("open");
        let file = wide(url);
        // SAFETY: 字符串都以 NUL 结尾并在调用期间存活
        unsafe {
            ShellExecuteW(
                std::ptr::null_mut(),
                operation.as_ptr(),
                file.as_ptr(),
                std::ptr::null(),
                std::ptr::null(),
                1, // SW_SHOWNORMAL
            );
        }
    }
}
