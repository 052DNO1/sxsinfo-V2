//! 桌面端应用配置（服务器地址）
//!
//! 配置文件位于系统标准的「应用配置目录」，Windows 下通常是：
//! `%APPDATA%\com.sxsinfo.lims.desktop\config.json`
//!
//! 之所以不放在 WebView 的 localStorage 里：
//! 配置文件可备份、可运维批量下发、可排查，而 localStorage 属于 WebView 数据，
//! 清理缓存就会丢，且用户与运维都看不到。

use std::fs;
use std::path::PathBuf;

use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Manager};

const FILE_NAME: &str = "config.json";

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
#[serde(rename_all = "camelCase")]
pub struct AppConfig {
    /// 后端 API 根地址，例如 `http://192.168.1.20:8000/api/v1`
    ///
    /// `None` 表示未配置，此时前端回落到构建时地址或内置默认值。
    pub api_base_url: Option<String>,
}

impl AppConfig {
    /// 配置文件绝对路径
    pub fn file_path(app: &AppHandle) -> Option<PathBuf> {
        app.path()
            .app_config_dir()
            .ok()
            .map(|dir| dir.join(FILE_NAME))
    }

    /// 读取配置；文件缺失或损坏一律回落到默认值（不让应用起不来）
    pub fn load(app: &AppHandle) -> Self {
        let Some(path) = Self::file_path(app) else {
            return Self::default();
        };

        let Ok(raw) = fs::read_to_string(&path) else {
            return Self::default();
        };

        match serde_json::from_str::<Self>(&raw) {
            Ok(mut config) => {
                config.normalize();
                config
            }
            Err(error) => {
                eprintln!("[config] 解析失败，使用默认配置: {error}");
                Self::default()
            }
        }
    }

    /// 写入配置
    pub fn save(&self, app: &AppHandle) -> Result<(), std::io::Error> {
        let Some(path) = Self::file_path(app) else {
            return Err(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                "无法定位应用配置目录",
            ));
        };

        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)?;
        }

        let json = serde_json::to_string_pretty(self)
            .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))?;
        fs::write(path, json)
    }

    /// 去掉空白、把空串视为未配置
    pub fn normalize(&mut self) {
        self.api_base_url = self
            .api_base_url
            .take()
            .map(|value| value.trim().to_string())
            .filter(|value| !value.is_empty());
    }

    /// 生成注入到 WebView 的初始化脚本
    ///
    /// 该脚本在页面任何脚本执行之前运行，因此前端的运行时配置层
    /// （`window.__LIMS_CONFIG__`）能同步拿到地址，不需要异步等待。
    pub fn initialization_script(&self) -> String {
        let payload = serde_json::json!({
            "apiBaseUrl": self.api_base_url,
        });

        format!(
            "window.__LIMS_DESKTOP__ = true;\nwindow.__LIMS_CONFIG__ = {payload};\n",
            payload = payload
        )
    }
}

/// 读取当前服务器配置（供前端设置页调用）
#[tauri::command]
pub fn get_server_config(app: AppHandle) -> AppConfig {
    AppConfig::load(&app)
}

/// 保存服务器地址（供前端设置页调用）
///
/// 传 `null` / 空串表示清除本机配置，回落到构建时地址。
#[tauri::command]
pub fn set_server_config(
    app: AppHandle,
    api_base_url: Option<String>,
) -> Result<AppConfig, String> {
    let mut config = AppConfig::load(&app);
    config.api_base_url = api_base_url;
    config.normalize();
    config.save(&app).map_err(|error| error.to_string())?;
    Ok(config)
}
