# Tauri 请求接管说明（现状报告）

> 报告对象：`desktop/`（Tauri 2 + 系统 WebView2 + Vue 3 前端）
> 结论一句话：**当前由前端 axios 接管请求（Tauri 两种方式里的第一种），Rust 侧不碰业务 HTTP。**
> 本报告所有判断都有 `文件:行` 证据，不是推断。

---

## 一、Tauri 架构下发请求的两种方式

| | 方式 A：前端直连（WebView 网络栈） | 方式 B：Rust 侧发送（reqwest / plugin-http） |
| --- | --- | --- |
| 谁发请求 | WebView2 内置 Chromium 网络栈 | Rust 进程（`tauri-plugin-http` 内部是 reqwest） |
| CORS | **生效**，需服务端放行 origin | **不适用**（Rust 不是浏览器） |
| cookie / session | 自动带，和网页一致 | 不带（除非手动搬） |
| DevTools 网络面板 | 可见，能看请求头/响应/耗时 | **不可见**，排障要自己造日志 |
| AbortController / 超时 / 进度 | 完整支持 | 受限 |
| 企业代理 / 客户端证书 / TLS 固定 | 按 WebView 规则，难干预 | **原生层能干净处理** |
| 页面能否读到 token | 能（XSS 风险面） | 可以不暴露给页面（1Password 式） |
| 适合 | **业务 CRUD**（本项目的全部场景） | 机密请求、后台同步、代理/证书场景 |

---

## 二、现状：本项目属于方式 A（证据）

| 事实 | 位置 |
| --- | --- |
| axios 实例（BaseURL / 超时） | `core/api/client.js:41` `axios.create({...})` |
| 请求拦截器自动带 Token | `core/api/client.js:105`、`:113` `Authorization = Bearer <token>` |
| 响应拦截器（401 刷新令牌后重放） | `core/api/client.js:134`、`:164` |
| 请求去重 / 排队 | `core/api/queue.js` |
| Token 读写 | `core/utils/tokenManager.js` + `core/api/client.js:84-102`（**sessionStorage**） |
| 连通性状态（延迟/离线） | `core/config/connection.js` → `useConnection()`（`isOnline` / `latencyMs` / `checkConnection`） |
| 底层服务层 / CRUD 链 | `core/services/BaseService.js` + `core/hooks/base/*` + `core/hooks/domain/*` |
| Rust 侧依赖 | `src-tauri/Cargo.toml`：只有 `tauri` + `serde`（外加外壳用的 `webview2-com` / `windows`）→ **没有 `tauri-plugin-http`、没有 `reqwest`** |

**因此当前的实际网络行为**：请求从 `http://tauri.localhost`（应用 origin）发往 `http://localhost:8000/api/v1/...`，
属于跨域 → 由后端 CORS 放行（现在能用即证明已配好）；OPTIONS 预检、证书校验、DevTools 可见性都按浏览器规则走。
`tauri.conf.json` 里 `app.security.csp: null`，请求走 WebView，**不需要任何 Tauri 特殊配置**。

---

## 三、大厂怎么放这一层

| 产品 | 形态 | 请求层 | 凭据存放 |
| --- | --- | --- | --- |
| VS Code | Electron | 业务在渲染进程 `fetch`，但经 `vscode-proxy-agent` 尊重系统代理/企业证书 | OAuth + 系统钥匙串 |
| Slack / Teams | Electron | 业务在渲染进程，**认证刷新走主进程 `net`** | `safeStorage`（Windows DPAPI / macOS Keychain） |
| Notion / Linear | Electron | 业务在渲染进程，桌面壳只管窗口/更新/快捷键 | `safeStorage`；Linear 的 access token 只在内存 |
| 1Password | Rust 核心 + Web UI | **机密请求全在 Rust**，页面拿不到 token | Rust 侧强保险库 |

归纳成决策表（也是本项目的取舍依据）：

```
业务 CRUD（列表/详情/提交）        → 前端 axios/fetch        ← 我们在这里
刷新令牌 / OAuth 换票              → 原生层（页面不该持有）
企业代理 / mTLS / 固定 TLS 指纹     → 原生层
后台同步 / 常驻轮询 / 离线队列      → 原生层
"只是为了绕 CORS"                  → 不这么做；自有 API 就在服务端配置 CORS
```

**关于 CORS，优先顺序是**：① 自有 API 服务端按 origin 放行（本项目现状，最优）→ ② 本地回环/自定义协议代理（Electron 常用）→ ③ 把请求搬到 Rust（最后手段）。

---

## 四、Token 存储的等级（本项目在第 ② 级）

```
① localStorage                     ← 最差，XSS 直接拿走        （本项目未使用 ✔）
② sessionStorage                   ← 现状：关窗即失效，但仍可被 JS 读取
③ 系统凭据管理器（DPAPI / Keychain / libsecret / stronghold）  ← 大厂标准
④ 页面完全不持有 token（原生层注入 Authorization）             ← 保险库级
```

已经做对的两条硬规矩：
- **短命 access + 长命 refresh**，401 时**单飞刷新**（一个刷新请求，其余请求排队重放）——`client.js:164` + `api/queue.js`；
- 刷新失败 → 清空状态 → 回登录页（路由守卫 + `authUtils`）。

---

## 五、如果将来要切成方式 B：只需改一处

业务代码（hooks / 拦截器 / 页面）**一行都不用动**，只换 axios 的传输适配器：

```js
// core/api/client.js —— 仅示意：把传输层换成 Tauri 的 Rust 请求
import { fetch as tauriFetch } from '@tauri-apps/plugin-http'

const api = axios.create({
  baseURL,
  timeout,
  // 用自定义 adapter 把 axios 的请求转交给 plugin-http
  adapter: async (config) => {
    const response = await tauriFetch(buildUrl(config), {
      method: config.method,
      headers: config.headers,
      body: config.data ? JSON.stringify(config.data) : undefined
    })
    return { data: await response.json(), status: response.status, headers: response.headers, config }
  }
})
```

同时需要在 `src-tauri/capabilities/default.json` 放开 `http:default` 与域名白名单。
**切换前必须接受的代价**：cookie/session 不再自动携带、DevTools 看不到这些请求、`AbortController` 与部分 axios 能力受限。

> 触发条件：只有当**后端无法配置 CORS**，或**校园网要求客户端证书/强制代理**时才切。目前两者都不成立。

---

## 六、现状清单

**已完成（本会话内）**
- 底部状态栏与真实请求联动：「已连接 · N ms」取自 `useConnection()` 的实测延迟；「共 N 条数据」取自表格 `total`；
- 断网不崩：`ConnectionGuard` 全屏接管 + 状态栏状态点变红；
- 表格加载态：`DataTable` 有 `v-loading`，请求中按钮禁用；
- 列表 CRUD 全链路（`useBaseList`/`useCRUD`/`useDelete` → `BaseService` → axios）；
- **全局快捷键（本次打包带入）**：`Ctrl/Cmd+K` 派发 `lims:global-search` 事件；`Ctrl/Cmd+R` 只重发当前表格请求（`statusStore.registerReload` 注册机制 + `DataTable` 注册 + `App.vue` 挂载），**不整页刷新**。

**待办（缺口，按性价比排序）**

| 缺口 | 内容 | 风险 | 说明 |
| --- | --- | --- | --- |
| A | refresh token 迁到 Windows 凭据管理器（②→③） | 中 | 需 `keyring` crate 或 `tauri-plugin-stronghold`；access token 只留内存 |
| B | 表格行操作的行内菜单可选切换为 Tauri 原生菜单 | 中 | 现有 HTML 菜单已支持贴边翻转与键盘，原生菜单样式不随主题 |
| C | `Ctrl+K` 的实际搜索面板接入（现在只派发事件） | 低 | 侧边栏搜索框/`GlobalSearch` 监听到事件后聚焦即可 |
| D | `core/api`、`core/store`、`core/hooks/base` 三层转 TypeScript | 中高 | 工程当前是纯 JS；建议只转这三层 + 定义 `types/api.d.ts` |
| E | 引入 `plugin-http` 替换 axios | **不建议** | 见第五节代价；仅在 CORS 无解时启用 |

**明确不建议做**：重写 `core/api/client.js`、把 token 全量搬进 Rust、用 `plugin-http` 替换 axios —— 这三件都会**降低**当前已稳定的能力（令牌刷新、请求去重、排障可见性）。

---

## 七、验收清单（可照着点）

1. 打开首页 → 状态栏出现「已连接 · N ms」，切到列表页 → 右侧出现「共 N 条数据」；
2. 把后端停掉 → 出现连接守卫页、状态栏点变红；此时按 `Ctrl+R` **不应导致整页白屏或崩溃**；
3. 列表页按 `Ctrl+R` → 只有表格出现 loading 并重新拉数据，**页面不重载**（滚动位置、侧边栏展开状态保持）；
4. 任意输入框内按 `Ctrl+R` → 不拦截（避免干扰输入）；
5. 按 `Ctrl+K` → 派发全局搜索事件（当前需搜索组件监听后才会弹面板，见缺口 C）；
6. 开发者工具 → Network 面板能看到所有业务请求（方式 A 的特征，换成方式 B 后将看不到）。
