//! 桌面外壳：无边框窗口 + 自绘标题栏所需的原生命令
//!
//! 【为什么要有这一层】
//! 系统标题栏 + 经典 Win32 菜单条是"网页套壳"最显眼的外壳特征。
//! 企业级桌面应用（VS Code / Teams / Slack / Linear 等）的通行做法是：
//! 去掉系统标题栏，用应用自绘的品牌标题栏承载「应用标识 + 全局操作 + 窗口按钮」。
//!
//! Windows 下没有 macOS 的 `titleBarStyle: overlay`，只能 `decorations: false`，
//! 于是原本由系统提供的四件事必须自己补上：
//!
//! 1. **拖动窗口**：自绘标题栏用 `start_dragging()` 驱动；
//! 2. **双击最大化 / 拖动到屏幕顶部贴靠**：双击由前端处理，贴靠交给系统；
//! 3. **圆角与描边**：Win11 用 DWM 的 `WINDOW_CORNER_PREFERENCE` / `BORDER_COLOR` 补，
//!    否则无边框窗口会变成 2010 年风格的直角方块；
//! 4. **窗口状态同步**：最大化/还原按钮的图标要跟着窗口状态变，靠事件回推给前端。
//!
//! 所有窗口操作都走本模块自己的命令，而不是 `core:window:*` 插件权限 —— 这样
//! `capabilities/default.json` 不需要放开多余的窗口权限面。

use tauri::{AppHandle, Emitter, WebviewWindow};

/// 切换为「系统标题栏 + 原生菜单栏」只需把这里改成 `false`
///
/// 两者取舍：
/// - `true`（当前）：外观与主流桌面应用一致，但菜单要应用内自绘、贴靠布局依赖系统实现；
/// - `false`：零风险，但一眼能看出是"窗口里嵌了个网页"。
pub const CUSTOM_CHROME: bool = true;

/// 前端监听的事件名
pub const EVENT_THEME: &str = "lims:theme";
pub const EVENT_WINDOW_STATE: &str = "lims:window-state";

/// 窗口自绘时要处理的动作
#[tauri::command]
pub fn shell_window(window: WebviewWindow, action: String) -> Result<(), String> {
    match action.as_str() {
        "minimize" => window.minimize().map_err(|error| error.to_string()),
        "toggle-maximize" => {
            let maximized = window.is_maximized().map_err(|error| error.to_string())?;
            if maximized {
                window.unmaximize().map_err(|error| error.to_string())
            } else {
                window.maximize().map_err(|error| error.to_string())
            }
        }
        "toggle-fullscreen" => {
            let fullscreen = window.is_fullscreen().map_err(|error| error.to_string())?;
            window
                .set_fullscreen(!fullscreen)
                .map_err(|error| error.to_string())
        }
        "close" => window.close().map_err(|error| error.to_string()),
        // 自绘标题栏的拖动：按下即把拖动交给系统，避免自己做位移导致卡顿/丢失贴靠
        "start-drag" => window.start_dragging().map_err(|error| error.to_string()),
        other => Err(format!("未知的窗口动作：{other}")),
    }
}

/// 应用内菜单：复用 `menu.rs` 里同一套菜单项 ID，逻辑不重复实现
#[tauri::command]
pub fn shell_menu(app: AppHandle, id: String) {
    crate::menu::handle_event(&app, &id);
}

/// 把当前窗口状态（是否最大化、当前主题）推给前端
fn window_state_payload(window: &WebviewWindow) -> serde_json::Value {
    let maximized = window.is_maximized().unwrap_or(false);
    let fullscreen = window.is_fullscreen().unwrap_or(false);
    serde_json::json!({ "maximized": maximized, "fullscreen": fullscreen })
}

/// 主动推送一次窗口状态（前端挂载后调用，避免首帧图标不对）
#[tauri::command]
pub fn shell_sync(window: WebviewWindow) -> serde_json::Value {
    window_state_payload(&window)
}

/// 窗口尺寸/状态变化时推送给前端
pub fn emit_window_state(window: &WebviewWindow) {
    let _ = window.emit(EVENT_WINDOW_STATE, window_state_payload(window));
}

/// 系统主题变化时推送给前端（前端据此切明暗，而不是自己轮询）
pub fn emit_theme(window: &WebviewWindow, theme: &str) {
    let _ = window.emit(EVENT_THEME, theme.to_string());
}

/// 主题字符串
pub fn theme_name(window: &WebviewWindow) -> &'static str {
    match window.theme() {
        Ok(tauri::Theme::Dark) => "dark",
        _ => "light",
    }
}

/// 无边框窗口的 Win11 修饰：圆角 + 细描边
///
/// 不做的话窗口是 2010 年那种直角方块，"企业级"三个字立刻掉一半。
/// 旧系统上 DWM 会直接返回错误，静默忽略即可。
pub fn apply_window_chrome(window: &WebviewWindow) {
    #[cfg(windows)]
    {
        use std::ffi::c_void;

        #[link(name = "dwmapi")]
        extern "system" {
            fn DwmSetWindowAttribute(
                hwnd: *mut c_void,
                attribute: u32,
                value: *const c_void,
                size: u32,
            ) -> i32;
        }

        let Ok(handle) = window.hwnd() else { return };
        let hwnd = handle.0 as *mut c_void;

        // DWMWA_WINDOW_CORNER_PREFERENCE = 33, DWMWCP_ROUND = 2
        let corner: u32 = 2;
        // SAFETY: 属性值大小与文档一致（DWORD）
        let _ = unsafe {
            DwmSetWindowAttribute(hwnd, 33, &corner as *const u32 as *const c_void, 4)
        };

        // 无边框窗口默认没有系统阴影，给一个极浅的描边把边界交代清楚
        // DWMWA_BORDER_COLOR = 34，COLORREF = 0x00BBGGRR
        let border: u32 = 0x00E6_E6E6; // #E6E6E6
        let _ = unsafe {
            DwmSetWindowAttribute(hwnd, 34, &border as *const u32 as *const c_void, 4)
        };
    }

    #[cfg(not(windows))]
    let _ = window;
}
