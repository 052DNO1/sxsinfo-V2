//! 原生菜单栏
//!
//! 桌面端区别于网页的一个基本特征。菜单只放真正有意义的操作，
//! 不堆砌占位项：
//!
//! - 文件 → 退出
//! - 视图 → 重新加载 / 开发者工具 / 全屏
//! - 帮助 → 服务器设置 / 关于（版本、运行时、配置与日志位置）
//!
//! 「开发者工具」对这套系统是有实际价值的：现场排查接口报错时，
//! 管理员可以直接打开控制台看到请求与错误，不需要装别的工具。
//! 为此 Cargo.toml 里显式开启了 tauri 的 `devtools` feature
//! （否则 release 构建里该菜单项不生效）。

use tauri::menu::{Menu, MenuItem, PredefinedMenuItem, Submenu};
use tauri::{AppHandle, Manager};

/// 菜单项标识，与事件处理一一对应
pub const MENU_RELOAD: &str = "lims.reload";
pub const MENU_DEVTOOLS: &str = "lims.devtools";
pub const MENU_SERVER_SETTINGS: &str = "lims.server-settings";
pub const MENU_ABOUT: &str = "lims.about";

/// 构建应用菜单
///
/// 失败不致命：上层只记录日志并跳过，不允许因为菜单出问题导致应用起不来。
pub fn build(app: &AppHandle) -> tauri::Result<Menu<tauri::Wry>> {
    let file_menu = Submenu::with_items(
        app,
        "文件",
        true,
        &[&PredefinedMenuItem::quit(app, Some("退出"))?],
    )?;

    let view_menu = Submenu::with_items(
        app,
        "视图",
        true,
        &[
            &MenuItem::with_id(app, MENU_RELOAD, "重新加载", true, Some("CmdOrCtrl+R"))?,
            &MenuItem::with_id(app, MENU_DEVTOOLS, "开发者工具", true, Some("F12"))?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::fullscreen(app, Some("全屏"))?,
        ],
    )?;

    let help_menu = Submenu::with_items(
        app,
        "帮助",
        true,
        &[
            &MenuItem::with_id(app, MENU_SERVER_SETTINGS, "服务器设置", true, None::<&str>)?,
            &PredefinedMenuItem::separator(app)?,
            &MenuItem::with_id(
                app,
                MENU_ABOUT,
                "关于 实训室信息管理系统",
                true,
                None::<&str>,
            )?,
        ],
    )?;

    Menu::with_items(app, &[&file_menu, &view_menu, &help_menu])
}

/// 处理菜单点击
pub fn handle_event(app: &AppHandle, id: &str) {
    // 「关于」不需要窗口，先处理掉
    if id == MENU_ABOUT {
        show_about(app);
        return;
    }

    let Some(window) = app.get_webview_window(crate::WINDOW_LABEL) else {
        return;
    };

    match id {
        MENU_RELOAD => {
            if let Err(error) = window.eval("window.location.reload()") {
                eprintln!("[menu] 重新加载失败: {error}");
            }
        }
        MENU_DEVTOOLS => {
            if window.is_devtools_open() {
                window.close_devtools();
            } else {
                window.open_devtools();
            }
        }
        MENU_SERVER_SETTINGS => {
            // 前端用的是 hash 路由，改 hash 即可跳转，无需重载页面
            if let Err(error) = window.eval("window.location.hash = '#/server-settings'") {
                eprintln!("[menu] 打开服务器设置失败: {error}");
            }
        }
        _ => {}
    }
}

/// 「关于」对话框
///
/// 内容刻意包含运维真正会问的四件事：版本、WebView2 运行时、服务器地址、配置与日志在哪。
/// 这些信息原先散落在日志与注册表里，现场打电话问"你装的是哪个版本"时很难答上来。
fn show_about(app: &AppHandle) {
    let config = crate::app_config::AppConfig::load(app);

    let api_base_url = config
        .api_base_url
        .unwrap_or_else(|| "（未配置，使用构建时地址或内置默认值）".to_string());

    let webview2 = crate::webview_health::runtime_version()
        .unwrap_or_else(|| "未检测到（桌面端需要它才能显示界面）".to_string());

    let config_dir = app
        .path()
        .app_config_dir()
        .map(|dir| dir.display().to_string())
        .unwrap_or_else(|_| "（无法定位）".to_string());

    let log_path = std::env::current_exe()
        .ok()
        .and_then(|exe| {
            exe.parent()
                .map(|dir| dir.join("startup.log").display().to_string())
        })
        .unwrap_or_else(|| "startup.log".to_string());

    let text = format!(
        "实训室信息管理系统（桌面端）\n\
         版本：{}    应用标识：{}\n\n\
         WebView2 运行时：{}\n\
         服务器地址：{}\n\n\
         配置文件目录：{}\n\
         启动日志：{}\n\n\
         技术栈：Rust + Tauri 2 + 系统 WebView2",
        env!("CARGO_PKG_VERSION"),
        app.config().identifier,
        webview2,
        api_base_url,
        config_dir,
        log_path
    );

    crate::show_info("关于 实训室信息管理系统", &text);
}
