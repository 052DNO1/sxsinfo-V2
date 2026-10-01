//! 主窗口位置与尺寸的持久化
//!
//! 不引入 `tauri-plugin-window-state`（未缓存），改为自己读写一个 JSON 文件，
//! 存放位置与服务器配置一致（应用配置目录），便于统一备份与排查。
//!
//! 关键取舍：**只在窗口未最大化时记录尺寸**，
//! 否则最大化状态下的尺寸会覆盖掉「还原」时应有的窗口大小。

use std::fs;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Manager, Window};

/// 默认窗口尺寸（首次启动）
pub const DEFAULT_WIDTH: f64 = 1440.0;
pub const DEFAULT_HEIGHT: f64 = 900.0;

/// 最小窗口尺寸，防止布局被压坏
pub const MIN_WIDTH: f64 = 1024.0;
pub const MIN_HEIGHT: f64 = 640.0;

const FILE_NAME: &str = "window-state.json";

#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(rename_all = "camelCase")]
pub struct WindowState {
    pub width: f64,
    pub height: f64,
    pub x: Option<f64>,
    pub y: Option<f64>,
    pub maximized: bool,
}

impl Default for WindowState {
    fn default() -> Self {
        Self {
            width: DEFAULT_WIDTH,
            height: DEFAULT_HEIGHT,
            x: None,
            y: None,
            maximized: false,
        }
    }
}

/// 内存中的窗口状态，随窗口事件更新，退出时落盘
static STATE: LazyLock<Mutex<WindowState>> = LazyLock::new(|| Mutex::new(WindowState::default()));

fn file_path(app: &AppHandle) -> Option<PathBuf> {
    app.path()
        .app_config_dir()
        .ok()
        .map(|dir| dir.join(FILE_NAME))
}

/// 读取已保存的窗口状态；文件缺失或损坏时回落到默认值
pub fn load(app: &AppHandle) -> WindowState {
    let Some(path) = file_path(app) else {
        return WindowState::default();
    };

    let Ok(raw) = fs::read_to_string(&path) else {
        return WindowState::default();
    };

    match serde_json::from_str::<WindowState>(&raw) {
        Ok(state) => {
            let state = sanitize(state);
            if let Ok(mut guard) = STATE.lock() {
                *guard = state.clone();
            }
            state
        }
        Err(error) => {
            eprintln!("[window-state] 解析失败，使用默认窗口尺寸: {error}");
            WindowState::default()
        }
    }
}

/// 纠正明显不合理的值（例如分辨率变化后窗口跑到屏幕外）
fn sanitize(mut state: WindowState) -> WindowState {
    if !state.width.is_finite() || state.width < MIN_WIDTH {
        state.width = DEFAULT_WIDTH;
    }
    if !state.height.is_finite() || state.height < MIN_HEIGHT {
        state.height = DEFAULT_HEIGHT;
    }
    if let Some(x) = state.x {
        if !x.is_finite() {
            state.x = None;
        }
    }
    if let Some(y) = state.y {
        if !y.is_finite() {
            state.y = None;
        }
    }
    state
}

/// 从窗口读取当前状态到内存
pub fn capture(window: &Window) {
    let Ok(mut guard) = STATE.lock() else { return };

    // 最大化/全屏时不覆盖还原尺寸
    let maximized = window.is_maximized().unwrap_or(false);
    guard.maximized = maximized;

    if !maximized {
        if let Ok(size) = window.inner_size() {
            let scale = window.scale_factor().unwrap_or(1.0);
            let logical = size.to_logical::<f64>(scale);
            if logical.width >= MIN_WIDTH && logical.height >= MIN_HEIGHT {
                guard.width = logical.width;
                guard.height = logical.height;
            }
        }
        if let Ok(position) = window.outer_position() {
            let scale = window.scale_factor().unwrap_or(1.0);
            let logical = position.to_logical::<f64>(scale);
            guard.x = Some(logical.x);
            guard.y = Some(logical.y);
        }
    }
}

/// 把内存中的状态写入磁盘
pub fn persist(app: &AppHandle) {
    let Some(path) = file_path(app) else { return };
    let Ok(guard) = STATE.lock() else { return };

    if let Some(parent) = path.parent() {
        let _ = fs::create_dir_all(parent);
    }

    match serde_json::to_string_pretty(&*guard) {
        Ok(json) => {
            if let Err(error) = fs::write(&path, json) {
                eprintln!("[window-state] 写入失败: {error}");
            }
        }
        Err(error) => eprintln!("[window-state] 序列化失败: {error}"),
    }
}
