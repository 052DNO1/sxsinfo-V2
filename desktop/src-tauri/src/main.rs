// 发布版不附带控制台窗口（调试版保留，方便看日志）
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    lims_desktop_lib::run()
}
