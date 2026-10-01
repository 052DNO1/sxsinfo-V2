# LIMS 桌面端（Tauri 2）

实训室信息管理系统的 Windows 桌面客户端。

**`desktop/` 是自包含的完整工程**：前端源码、Rust 外壳、图标、打包配置全部在里面。
可以单独改动、单独构建、单独压缩给别人，不依赖 `desktop/` 之外的任何路径。

---

## 一、目录结构

```
desktop/
├── frontend/                    # 前端源码（桌面端自己的一份，可直接改）
│   ├── src/
│   ├── index.pc.html
│   ├── vite.config.pc.js
│   ├── package.json
│   └── dist/pc/                 # 构建产物（自动生成，不入库）
├── src-tauri/                   # Rust 外壳
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   ├── capabilities/default.json
│   ├── icons/                   # 成品图标（.ico / .icns / 各尺寸 PNG）
│   └── src/
│       ├── main.rs              # 进程入口
│       ├── lib.rs               # 窗口创建、事件、命令注册
│       ├── menu.rs              # 原生菜单栏
│       ├── app_config.rs        # 服务器地址读写 + 注入
│       ├── single_instance.rs   # 单实例（自实现，无插件依赖）
│       └── window_state.rs      # 窗口位置/尺寸持久化（自实现）
└── scripts/
    ├── sync-frontend.ps1        # 从原 frontend 目录拉取更新
    └── generate-icon.py         # 重新生成图标源图
```

---

## 二、首次准备：把前端源码复制进来

### 复制清单

| 项 | 值 |
| --- | --- |
| **源目录** | `frontend\` |
| **目标目录** | `desktop\frontend\` |
| **要复制的** | 下列 14 项，目录结构保持原样 |
| **不要复制的** | `node_modules\`（重装）、`dist\`（本地构建） |

> ⚠ **复制的是 `frontend\` 里面的内容，不是 `frontend` 这个文件夹本身。**
> 正确结果：`desktop\frontend\src\`、`desktop\frontend\package.json`
> 错误结果：`desktop\frontend\frontend\src\`（多套了一层，构建会失败）

**要复制的 14 项：**

```
src\                   ← 整个目录，160 个文件 / 1.49 MB（最重要）
index.html
index.pc.html          ← PC 端入口
index.mobile.html
vite.config.pc.js      ← PC 端构建配置
vite.config.mobile.js
package.json
yarn.lock
jsconfig.json
.env                   ← 含 VITE_PASSWORD_ENCRYPT_KEY，必须与后端一致
.eslintrc.cjs
.eslintignore
Dockerfile.pc
Dockerfile.mobile
```

合计约 **173 个文件 / 1.6 MB**。

> 用脚本做等价（推荐，省得漏文件）：
> ```powershell
> cd desktop
> .\scripts\sync-frontend.ps1 -Source ..\frontend
> ```

**必须一起复制的关键三项**：`src\`、`index.pc.html`、`vite.config.pc.js`。
少了任何一个都构建不出来。

### 然后装依赖

```powershell
cd desktop\frontend
yarn install
```

**必须用 `yarn install`，不要用 `npm install`。**

理由：项目只有 `yarn.lock`，没有 `package-lock.json`。
npm 没有锁文件可依，会按 `package.json` 里的 `^` 版本范围**重新解析**依赖
（例如 `element-plus: ^2.11.8` 可能装到 2.13.x 或将来更高的次版本）。
那样桌面端装到的依赖就和已验证的 Web 端不是同一套，会出现「同一份代码两边表现不一样」的诡异问题。
yarn 严格按锁文件还原，能保证与 Web 端完全一致。

本机 yarn 缓存约 3.2 GB，正常可离线装完。

`node_modules` 是 22,311 个文件 / 257 MB，所以不建议从 `frontend\node_modules` 手工复制（很慢）。

---

## 三、开发与打包

```powershell
cd desktop\src-tauri

# 开发运行：会自动启动 desktop/frontend 的 vite 开发服务器（热重载）
cargo tauri dev

# 出安装包（MSI + NSIS）
cargo tauri build
```

产物：

| 类型 | 路径 |
| --- | --- |
| 可执行文件 | `src-tauri\target\release\lims-desktop.exe`（文件名取自 `Cargo.toml` 的 `package.name`，与 `productName` 无关） |
| MSI 安装包 | `src-tauri\target\release\bundle\msi\*.msi` |
| NSIS 安装包 | `src-tauri\target\release\bundle\nsis\*-setup.exe` |

### ⚠ 必须用 `cargo tauri build`，不要用 `cargo build`

Tauri 在**编译期**把 `frontend/dist/pc` 的资源嵌入 exe。
`cargo tauri build` 会先跑 `beforeBuildCommand`（即 `yarn --cwd frontend build:pc`）再编译；
直接 `cargo build` 会嵌入上一次的旧产物，或者因产物不存在而失败。

### 怎么确认 exe 里真的嵌入了前端

exe 的资源清单以明文形式存在，前端文件名理应能搜到：

```powershell
findstr /M /C:"assets/" src-tauri\target\release\lims-desktop.exe
```

**搜不到就说明这次构建没有嵌进前端资源**，运行起来必然是白屏：
窗口标题正常、内容区一片纯白，而且进程不会派生出 `msedgewebview2.exe`。
此时用 `cargo tauri build` 重新构建即可。
（实测：漏嵌的 exe 里搜不到任何 `assets/`；正常构建的 exe 里有 130 余处。）

### 只改前端时

```powershell
cd desktop\frontend
yarn build:pc              # 或直接交给 cargo tauri build 自动做
```

---

## 四、两份前端代码的关系

`desktop/frontend/` 是从 `frontend/` 复制出来的一份**独立源码**，
好处是可以在桌面端直接改、直接构建。代价是**改动不会自动同步**：

| 场景 | 需要做什么 |
| --- | --- |
| 在桌面端改前端 | 直接改 `desktop\frontend\`，不受影响 |
| 原 `frontend/` 修了 bug，想同步过来 | `.\scripts\sync-frontend.ps1 -Source ..\frontend` |
| 桌面端前端改乱了，想退回与原前端一致 | 同上，加 `-Mirror`（会删除桌面端独有文件） |

> 这是「可独立修改」必然要付出的代价。若哪天觉得两份代码难维护，
> 正确的收敛方式是改成 monorepo（一个前端包，web 与桌面端都引用它），
> 而不是用软连接把两个目录接起来——那在压缩、换机器、进 CI 时都会断。

### ⚠ 桌面端前端有一处**有意的**配置差异

`desktop/frontend/vite.config.pc.js` 里多了 `build.target: 'esnext'`，
而原 `frontend/` 没有。**不要为了"两边保持一致"把它删掉**，删了桌面端就构建不出来。

原因：Vite 的 `vite:esbuild-transpile` 插件（仅非 `esnext` 目标启用）会让 esbuild
把整段 chunk 写进 `%TEMP%\esbuild-<hex>` 再删除，而这一步在 Windows 上对
`desktop/frontend` 稳定报 `Access is denied`，导致构建 100% 失败。
实测 `chrome120` / `chrome100` / `es2020` / `es2022` 全部失败，**仅 `esnext` 成功**
（该目标下插件被整个跳过）。

对桌面端可以接受，因为 WebView2 是版本已知且持续更新的 Chromium 内核（本机 154），
本来就不存在需要兼容老旧浏览器的问题。

影响范围仅限 `desktop/frontend` 这一份副本，**Web 端部署行为完全不变**。

---

## 五、服务器地址是怎么定的

### 优先级（从高到低）

1. **桌面端配置文件** —— `%APPDATA%\com.sxsinfo.lims.desktop\config.json`
2. **WebView 本机存储** —— 设置页写入的 `localStorage`
3. **构建时注入** —— 前端构建时的 `VITE_API_V2_BASE_URL`
4. **内置默认值** —— `http://localhost:8000/api/v1`

### 注入时机

Rust 在**创建窗口时**用 `initialization_script` 注入：

```js
window.__LIMS_DESKTOP__ = true
window.__LIMS_CONFIG__ = { apiBaseUrl: "..." }
```

该脚本先于页面内所有脚本执行，前端运行时配置层能**同步**读到地址，
不需要异步等待、也不会有请求抢跑。

### 修改地址

- 应用内：登录页右上角"服务器设置"，或直接访问 `#/server-settings`
- 手工改：编辑 `%APPDATA%\com.sxsinfo.lims.desktop\config.json` 后重启
- 批量下发：把该 json 推到各机器同一路径即可（私有化部署常用做法）

---

## 六、已实现的外壳能力

| 能力 | 实现方式 |
| --- | --- |
| 原生菜单栏 | 文件→退出；视图→重新加载 / 开发者工具 / 全屏；帮助→服务器设置 |
| 单实例 | **命名互斥体 + 命名事件**（`Local\com.sxsinfo.lims.desktop.*`，按登录会话隔离）；重复启动会把已有窗口提到前台。**不再占用 TCP 端口**——端口会被无关程序占用、异常退出留 TIME_WAIT，而且卡死的实例会一直占着它导致后续双击静默退出 |
| 窗口状态 | 位置/尺寸/最大化写入 `window-state.json`，启动时恢复 |
| 配置持久化 | 服务器地址写入系统应用配置目录的 `config.json` |
| 配置注入 | 窗口创建时注入，先于页面脚本 |
| 连接失败处理 | 连接守卫接管界面：重试 / 改地址 / 仍然继续 |
| 启动自检 | WebView2 超时未就绪则写启动日志 + 弹中文原生错误框，并以退出码 2 结束；超时可用 `LIMS_WEBVIEW_TIMEOUT_MS` 调整（默认 30 秒） |
| 运行期失败监听 | 接官方 `CoreWebView2.ProcessFailed`：**渲染进程崩** → 记日志 + 自动重载页面（同会话最多 3 次）；**浏览器进程退出** → 判定不可自愈，弹框并退出码 2；**无响应**只记一次日志（官方会重复上报，不能据此杀进程） |
| 运行时版本探测 | 启动时读 `pv`（HKLM/HKCU）写进日志；未安装时错误框会直接说明"未安装 WebView2 运行时" |
| 启动日志 | `%LOCALAPPDATA%\com.sxsinfo.lims.desktop\startup.log`；写不进去依次退到 **exe 同级**、系统临时目录 |
| 无控制台窗口 | release 构建 `windows_subsystem = "windows"` |
| 安装包 | MSI + NSIS（简体中文，perMachine）。两者都**内建 WebView2 检测与安装**（读 `pv` → 缺则装）；`downloadBootstrapper`（默认，需联网）／`embedBootstrapper`（+1.8 MB）／`offlineInstaller`（+127 MB，**离线部署用这个**）／`fixedRuntime`（+180 MB，版本完全自控） |

### 刻意不用的东西

- **`tauri-plugin-single-instance` / `tauri-plugin-window-state`**：引入它们会把构建绑死在网络上
  （本机 cargo 缓存里没有）。这两个功能自实现只需几十行，行为完全可控。
- **`tauri-plugin-shell`**：桌面端不需要执行任意系统命令，少一个插件少一份攻击面。

### 关于「开发者工具」菜单项

`Cargo.toml` 里显式开启了 tauri 的 `devtools` feature，否则 release 构建里该菜单项不生效。
保留它是刻意的：这套系统现场排查接口报错时，管理员能直接打开控制台看请求与错误，
不需要额外装工具。若不希望终端用户看到，删掉 `features = ["devtools"]` 与 `menu.rs` 中对应项即可。

菜单构建失败**不会导致应用起不来**：`lib.rs` 里只记录日志并跳过。

---

## 七、环境要求（本机已具备）

| 组件 | 版本 |
| --- | --- |
| Rust | 1.89 |
| tauri-cli | 2.10.1 |
| Node.js | 24.13 |
| WebView2 Runtime | 154.x |
| MSVC 工具链 | VS 2026（含 C++ 桌面开发） |
| WiX / NSIS | 已缓存于 `%LOCALAPPDATA%\tauri`，打包无需联网 |

**WebView2 是唯一的硬依赖**：它由 Windows / Edge 自动更新维护，不需要随包分发，
但它的健康状况决定了应用能否显示界面。本机该组件一旦异常，应用会走上面的启动自检
（弹中文错误框 + 写日志），不会再出现"白窗口"或"双击没反应"这种无从下手的状态。

---

## 八、常见问题

**`cargo tauri dev` 报找不到 frontend / yarn 报错**
→ 没复制前端源码，或没在 `desktop\frontend` 里执行 `yarn install`。

**界面白屏**
→ 打开开发者工具看报错。打包场景下多半是用了 `cargo build` 而非 `cargo tauri build`。

**窗口标题正常但内容全白 / 双击了"没反应"**
→ 这是 **WebView2 组件起不来**的典型表现，与本应用的数据无关。此时应用会在
`LIMS_WEBVIEW_TIMEOUT_MS`（默认 30 秒）后弹出中文错误框并写启动日志，不再是白窗口。
典型成因与处置：

1. 本机 WebView2 运行时损坏：重启电脑，或修复/重装「Microsoft Edge WebView2 运行时」。
2. 想看证据：事件查看器 → Windows 日志 → 应用程序，查找 `msedgewebview2.exe` 的
   Application Error；实测过一类是 `msedge_elf.dll` + 异常码 `0x80000003`，
   此时连一个 `msedgewebview2.exe` 子进程都留不下来。
3. 已排除的方向（不必再试）：`--disable-features` 参数、应用数据目录权限、兼容性垫片、
   `AppInit_DLLs`、杀软注入。这三种参数变体（wry 默认 / 仅 msSmartScreenProtection /
   不传参数）实测表现完全相同。
4. 交叉验证：同一台机器上**新启动**另一个 WebView2 应用（例如把 GameViewer 完全退出后重开）
   也会失败，即可确认是机器级问题而不是本应用。
5. **实测结论（2026-09-30 已复现并解决）**：机器级运行时（HKLM 登记的那一份）损坏时，
   应用侧**无法绕过**（试过 `--disable-features` 三种变体、强制指定运行时目录，均无效）；
   **重启电脑**让 EdgeUpdate 把它替换成用户级新版本后立即恢复。完整证据与时间线见
   `启动失败排查记录.md`。

**双击没任何反应、也不弹框**
→ 先看任务管理器有没有残留的 `lims-desktop.exe`：它可能占着单实例端口 51739 卡住了，
后面的启动都会静默退出。结束该进程再启动即可（新版已有看门狗，不会再无限卡住）。

**开发时每次都会弹出一个浏览器标签页**
→ 原 `vite.config.pc.js` 里写了 `server.open: '/index.html'`。
桌面端自带 WebView，这个自动打开是多余的，可以按需删掉该行。

**提示"无法连接到服务器"**
→ 点"服务器设置"确认地址；后端默认在 `http://localhost:8000`。

**改了前端代码但桌面端没变**
→ 开发模式（`cargo tauri dev`）有热重载；打包场景需要重新 `cargo tauri build`。
