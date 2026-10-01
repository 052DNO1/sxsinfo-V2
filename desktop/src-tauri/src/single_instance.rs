//! 单实例控制
//!
//! 【Windows 实现】用内核对象，不占用任何网络端口：
//! - 命名互斥体 `Local\com.sxsinfo.lims.desktop.single-instance` —— 判定"我是不是第一个实例"；
//! - 命名事件 `Local\com.sxsinfo.lims.desktop.activate` —— 后启动的实例用它唤醒已有实例，
//!   已有实例收到后把窗口提到前台。
//!
//! 【为什么换掉原先的"回环端口 + 握手"】
//! 端口是全局共享资源：可能被无关程序占用，异常退出后还可能留下 TIME_WAIT。
//! 更麻烦的是——**卡死的实例会一直占着端口**，导致之后每次双击都静默退出，
//! 现场表现就是"双击没反应"（本次排查就踩了这个）。
//! 内核对象是进程级句柄：进程一退，句柄由系统回收。这也是 Electron
//! (`requestSingleInstanceLock`) 与 Chromium 这类实现的常规做法。
//! 用 `Local\` 前缀表示按登录会话隔离：同一台机器上不同用户各开各的实例。
//!
//! 【非 Windows】保留原来的回环端口实现，保证这份 lib 仍能被移动端交叉编译（本项目只发布 Windows）。

use std::sync::mpsc::Receiver;

pub enum AcquireResult {
    /// 本进程是唯一实例；Receiver 在有新实例启动时收到通知
    Primary(Receiver<()>),
    /// 已有实例在运行，本进程应尽快退出
    Secondary,
    /// 无法判定（创建内核对象/绑定端口失败）：放弃单实例保护，照常启动
    Unavailable,
}

#[cfg(windows)]
mod platform {
    use std::ffi::c_void;
    use std::sync::mpsc::channel;

    use super::AcquireResult;

    /// 互斥体名（`Local\` = 按登录会话隔离）
    const MUTEX_NAME: &str = "Local\\com.sxsinfo.lims.desktop.single-instance";
    /// 激活事件名
    const EVENT_NAME: &str = "Local\\com.sxsinfo.lims.desktop.activate";

    const ERROR_ALREADY_EXISTS: u32 = 183;
    const EVENT_MODIFY_STATE: u32 = 0x0002;
    const WAIT_OBJECT_0: u32 = 0x0000_0000;
    /// 事件监听的轮询间隔：只为让线程状态可观察，不需要精确
    const WAIT_SLICE_MS: u32 = 500;

    #[link(name = "kernel32")]
    extern "system" {
        fn CreateMutexW(attributes: *mut c_void, initial_owner: i32, name: *const u16)
            -> *mut c_void;
        fn CreateEventW(
            attributes: *mut c_void,
            manual_reset: i32,
            initial_state: i32,
            name: *const u16,
        ) -> *mut c_void;
        fn OpenEventW(desired_access: u32, inherit_handle: i32, name: *const u16) -> *mut c_void;
        fn SetEvent(handle: *mut c_void) -> i32;
        fn WaitForSingleObject(handle: *mut c_void, milliseconds: u32) -> u32;
        fn CloseHandle(handle: *mut c_void) -> i32;
        fn GetLastError() -> u32;
    }

    fn wide(text: &str) -> Vec<u16> {
        text.encode_utf16().chain(std::iter::once(0)).collect()
    }

    pub fn acquire() -> AcquireResult {
        let mutex_name = wide(MUTEX_NAME);

        // SAFETY: 名称缓冲区在本次调用期间存活；返回的句柄由本函数接管
        let mutex = unsafe { CreateMutexW(std::ptr::null_mut(), 0, mutex_name.as_ptr()) };
        if mutex.is_null() {
            eprintln!("[single-instance] 创建互斥体失败，放弃单实例保护");
            return AcquireResult::Unavailable;
        }

        // GetLastError 必须紧接在 CreateMutexW 之后读，中间不能插入其他 Win32 调用
        let already_running = unsafe { GetLastError() } == ERROR_ALREADY_EXISTS;

        if already_running {
            // 已有实例：请它把窗口提到前台，本进程立刻退出
            let event_name = wide(EVENT_NAME);
            let event = unsafe { OpenEventW(EVENT_MODIFY_STATE, 0, event_name.as_ptr()) };
            if event.is_null() {
                eprintln!("[single-instance] 已有实例在运行，但激活事件打不开（可能它刚启动）");
            } else {
                unsafe {
                    SetEvent(event);
                    CloseHandle(event);
                }
            }
            unsafe { CloseHandle(mutex) };
            return AcquireResult::Secondary;
        }

        // 首个实例：建激活事件并常驻监听
        let event_name = wide(EVENT_NAME);
        let event = unsafe { CreateEventW(std::ptr::null_mut(), 0, 0, event_name.as_ptr()) };
        if event.is_null() {
            eprintln!("[single-instance] 创建激活事件失败，重复启动将无法唤醒本窗口");
            return AcquireResult::Unavailable;
        }

        let (tx, rx) = channel::<()>();
        // 句柄本身不是 Send，转成整数地址再交给线程（进程存活期间句柄始终有效）
        let event_address = event as usize;
        std::thread::spawn(move || {
            let event = event_address as *mut c_void;
            loop {
                // 没有退出条件是有意的：该线程随进程存活，句柄由系统在进程结束时回收
                if unsafe { WaitForSingleObject(event, WAIT_SLICE_MS) } == WAIT_OBJECT_0
                    && tx.send(()).is_err()
                {
                    return;
                }
            }
        });

        // 注意：mutex / event 句柄**故意不关闭** —— 首个实例必须持有它们到进程结束
        AcquireResult::Primary(rx)
    }
}

#[cfg(not(windows))]
mod platform {
    //! 非 Windows：保留回环端口 + 握手的自实现（本项目只发布 Windows 桌面端）

    use std::io::{BufRead, BufReader, Write};
    use std::net::{Ipv4Addr, SocketAddr, TcpListener, TcpStream};
    use std::sync::mpsc::channel;
    use std::thread;
    use std::time::Duration;

    use super::AcquireResult;

    const PORT: u16 = 51_739;
    const HANDSHAKE: &str = "LIMS-DESKTOP-ACTIVATE";
    const HANDSHAKE_ACK: &str = "LIMS-DESKTOP-OK";
    const IO_TIMEOUT: Duration = Duration::from_millis(800);

    fn addr() -> SocketAddr {
        SocketAddr::from((Ipv4Addr::LOCALHOST, PORT))
    }

    fn try_activate() -> bool {
        let Ok(mut stream) = TcpStream::connect_timeout(&addr(), IO_TIMEOUT) else {
            return false;
        };
        let _ = stream.set_read_timeout(Some(IO_TIMEOUT));
        let _ = stream.set_write_timeout(Some(IO_TIMEOUT));

        if stream
            .write_all(format!("{HANDSHAKE}\n").as_bytes())
            .is_err()
        {
            return false;
        }
        let _ = stream.flush();

        let mut reader = BufReader::new(stream);
        let mut line = String::new();
        if reader.read_line(&mut line).is_err() {
            return false;
        }

        line.trim() == HANDSHAKE_ACK
    }

    pub fn acquire() -> AcquireResult {
        if try_activate() {
            return AcquireResult::Secondary;
        }

        match TcpListener::bind(addr()) {
            Ok(listener) => {
                let (tx, rx) = channel::<()>();
                thread::spawn(move || {
                    for stream in listener.incoming() {
                        let Ok(mut stream) = stream else { continue };
                        let Ok(read_half) = stream.try_clone() else {
                            continue;
                        };

                        let mut line = String::new();
                        if BufReader::new(read_half).read_line(&mut line).is_err() {
                            continue;
                        }

                        if line.trim() == HANDSHAKE {
                            let _ = stream.write_all(format!("{HANDSHAKE_ACK}\n").as_bytes());
                            let _ = stream.flush();
                            let _ = tx.send(());
                        }
                    }
                });
                AcquireResult::Primary(rx)
            }
            Err(_) => AcquireResult::Unavailable,
        }
    }
}

pub use platform::acquire;
