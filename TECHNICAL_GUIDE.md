# LIMS V2 技术架构与操作指南

> **版本**: 2.0.0 | **最后更新**: 2026-04-26 | **项目代号**: 实训室信息管理系统 V2

---

## 一、系统总览与技术选型矩阵

### 1.1 架构拓扑

本系统采用**前后端分离 + 容器化微服务编排 + 多端适配**的混合架构模式，由五个核心子工程协同构成：

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户访问层                                │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ PC 浏览器 │  │ 移动端 Web   │  │ Android 原生 (Tauri)     │  │
│  │ Element+ │  │ Vant 4       │  │ WebView + Rust Runtime   │  │
│  └────┬─────┘  └──────┬───────┘  └──────────┬───────────────┘  │
│       │               │                      │                  │
└───────┼───────────────┼──────────────────────┼──────────────────┘
        ▼               ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx 反向代理网关 (:80/:443)                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ UA检测 → PC(/) | Mobile(/m/) | API(/api/) → upstream     │  │
│  │ 静态资源缓存(1y) | Gzip压缩 | WebSocket代理 | SSL终止     │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐ ┌──────────────┐ ┌────────────────────┐
│ Frontend-PC   │ │Frontend-Mobile│ │ Django Backend    │
│ dist/pc/      │ │ dist/mobile/  │ │ Gunicorn(:8000)   │
│ Vite Build    │ │ Vite Build    │ │ DRF + JWT Auth    │
└───────────────┘ └──────────────┘ └───────┬────────────┘
                                          │
                              ┌───────────┼───────────┐
                              ▼           ▼           ▼
                       ┌──────────┐ ┌─────────┐ ┌──────────┐
                       │ MySQL 8.0│ │ Redis 7 │ │ Celery   │
                       │ InnoDB   │ │ Cache   │ │ Async    │
                       └──────────┘ └─────────┘ └──────────┘
```

### 1.2 技术栈全景表

| 层级 | 技术组件 | 版本 | 核心职责 |
|------|---------|------|---------|
| **前端框架** | Vue 3 (Composition API) | 3.5.x | 响应式UI、组件化开发 |
| **PC UI库** | Element Plus | 2.11.x | 企业级桌面组件体系 |
| **Mobile UI库** | Vant 4 | 4.9.x | 移动端触控优化组件 |
| **构建工具** | Vite 7 | 7.1.x | ESM原生构建、HMR热更新 |
| **状态管理** | Pinia 3 | 3.0.x | 轻量级全局状态仓库 |
| **HTTP客户端** | Axios 1.x | 1.13.x | 拦截器队列化请求管理 |
| **图表引擎** | ECharts 5 + vue-echarts 6 | 5.5/6.6 | 多维度数据可视化 |
| **搜索引擎** | FlexSearch | 0.8.x | 前端全文索引与检索 |
| **表格处理** | SheetJS (xlsx) | 0.18.x | Excel导入导出解析 |
| **加密库** | CryptoJS | 4.2.x | 前端AES对称加密 |
| **后端框架** | Django 4.2 | 4.2.x | MTV架构、ORM、Admin |
| **API框架** | Django REST Framework | 3.14.x | 序列化器、视图集、路由 |
| **认证方案** | SimpleJWT | 5.3.x | Access/Refresh双Token轮换 |
| **数据库** | MySQL 8.0 | 8.0+ | InnoDB引擎、utf8mb4字符集 |
| **缓存层** | Redis 7 + django-redis | 7.x/5.4 | 会话存储、缓存策略、发布订阅 |
| **异步任务** | Celery 5.3 | 5.3.x | 后台任务队列（备份/AI等） |
| **WSGI服务器** | Gunicorn + Gevent | 21.x/23.9 | 高并发协程工作模型 |
| **反向代理** | Nginx (stable-alpine) | latest | 负载均衡、静态托管、SSL |
| **容器化** | Docker Compose 3.8 | - | 六容器服务编排 |
| **移动端打包** | Tauri 2 + Rust | 2.x | 原生Android壳WebView嵌入 |
| **API文档** | drf-spectacular | 0.27.x | OpenAPI 3.0 / Swagger UI |

---

## 二、backend-v2 — Django REST API 后端深度解析

### 2.1 项目结构与技术分层

```
backend-v2/
├── lims/                          # Django项目配置核心
│   ├── settings/
│   │   ├── base.py                # 基础配置（中间件、认证、日志、JWT）
│   │   ├── development.py         # 开发环境（DEBUG=True、本地DB）
│   │   ├── production.py          # 生产环境（安全加固、CORS限制）
│   │   └── testing.py             # 测试环境（内存数据库、Mock）
│   ├── urls.py                    # 主路由：admin + api/v1 + swagger
│   ├── wsgi.py                    # WSGI入口（Gunicorn绑定）
│   └── asgi.py                    # ASGI入口（WebSocket支持预留）
│
├── apps/                          # 业务应用域（DDD分层）
│   ├── core/                      # 【基础域】操作日志、异常中间件、统计中间件
│   │   ├── models.py              # BaseModel(TimeStamped+SoftDelete)+OperationLog
│   │   ├── middleware/            # ExceptionMiddleware / LoggingMiddleware / ApiStatsMiddleware
│   │   └── services/              # operation_log_service.py
│   │
│   ├── users/                     # 【用户域】RBAC权限体系
│   │   ├── models/user.py         # 自定义User模型（继承AbstractUser）
│   │   ├── models/department.py   # 部门树形结构（django-mptt）
│   │   ├── serializers/auth.py    # 登录/注册/Token刷新序列化器
│   │   ├── services/auth_service.py # JWT签发、密码AES加解密
│   │   └── views/auth.py          # 登录、登出、Token刷新端点
│   │
│   ├── laboratories/              # 【实训室域】实验室+设备管理
│   │   ├── models/laboratory.py   # Laboratory模型（工位数、状态枚举）
│   │   ├── models/equipment.py    # Equipment模型（配置JSONField）
│   │   ├── services/conflict_checker.py  # 排课冲突检测算法
│   │   └── services/summary_service.py   # 数据聚合统计
│   │
│   ├── schedules/                 # 【排课域】学期+课程+周次节次
│   │   ├── models/schedule.py     # Schedule模型（星期、节次、周次范围）
│   │   ├── models/semester.py     # Semester模型（当前学期标记）
│   │   ├── models/archive.py      # TermArchive归档模型
│   │   └── services/conflict_checker.py  # 时间冲突+教室冲突双重检测
│   │
│   ├── records/                   # 【记录域】使用记录填报
│   ├── maintenance/               # 【工单域】维护流程闭环
│   │   └── services/work_order_center_service.py  # 工单中心聚合查询
│   ├── notifications/             # 【通知域】消息推送
│   ├── ai_assistant/              # 【AI域】DeepSeek大模型集成
│   ├── backup/                    # 【备份域】定时备份+恢复
│   │   └── services/auto_backup_service.py  # Celery周期任务
│   ├── statistics/                # 【统计域】仪表盘多维数据
│   └── cache_config/              # 【配置域】Redis缓存策略管理
│
├── common/                        # 跨领域公共设施
│   ├── services/cache_service.py  # ★ 缓存管理体系（详见2.3节）
│   ├── services/export_service.py # Excel/PDF导出引擎
│   ├── services/import_service.py # Excel批量导入解析
│   ├── services/search_service.py # 全文搜索封装
│   ├── services/progress_service.py # 长任务进度追踪
│   ├── decorators.py              # 权限装饰器、日志装饰器
│   ├── paginations.py             # StandardPagination（Cursor+Offset混合）
│   ├── exceptions.py              # 统一异常响应格式
│   ├── responses.py               # 统一成功响应包装
│   ├── filters.py                 # 自定义DjangoFilterBackend扩展
│   ├── validators.py              # 字段级业务校验器
│   ├── enums.py                   # 枚举常量定义
│   └── mixins.py                  # ViewSet Mixin复用
│
├── extensions/                    # 基础设施扩展
│   ├── celery_app.py              # Celery应用实例（autodiscover_tasks）
│   └── redis_client.py            # Redis连接池封装
│
├── api/v1/                        # API版本化路由入口
│   └── urls.py                    # include各app的urls.py
│
├── requirements/                  # 依赖分层管理
│   ├── base.txt                   # 核心运行时依赖
│   ├── development.txt            # 开发额外依赖(debug-toolbar等)
│   ├── production.txt             # 生产额外依赖(gunicorn+gevent)
│   └── testing.txt                # 测试依赖(pytest+factory-boy)
│
├── tests/                         # 三层测试金字塔
│   ├── unit/                      # 单元测试（Models/Serializers/Services）
│   ├── integration/               # 集成测试（API端到端CRUD）
│   └── e2e/                       # 端到端测试（完整业务流）
│
├── scripts/                       # 运维脚本（数据校验/初始化/生成）
├── Dockerfile                     # 多阶段构建（Python slim → 生产镜像）
├── entrypoint.sh                  # 容器启动入口（迁移+收集静态+启动Gunicorn）
└── manage.py                      # Django管理命令入口
```

### 2.2 核心技术机制详解

#### 2.2.1 认证与安全体系

**JWT双Token机制**（[base.py:117-127](backend-v2/lims/settings/base.py#L117-L127)）：
```
Access Token:  有效期 2小时  → 携带于每次API请求 Header
Refresh Token: 有效期 7天   → 用于刷新Access Token
轮换策略:       ROTATE_REFRESH_TOKENS = True（每次刷新旧Token失效）
黑名单:         BLACKLIST_AFTER_ROTATION = True（防止Token重放）
签名算法:       HS256
```

**密码加密流程**：
```
用户注册/修改密码
  → 前端CryptoJS AES加密（VITE_PASSWORD_ENCRYPT_KEY）
  → HTTP传输密文
  → 后端pycryptodome AES解密
  → Django make_password() bcrypt哈希
  → 存储至MySQL
```

**自定义用户模型**：`AUTH_USER_MODEL = 'users.User'`，扩展字段包括 nickname、role、department、phone 等。

#### 2.2.2 中间件管道（执行顺序）

```python
MIDDLEWARE = [
    'SecurityMiddleware',           # 1. 安全头（HSTS、XSS过滤）
    'CorsMiddleware',               # 2. CORS跨域（配置ALLOWED_ORIGINS）
    'SessionMiddleware',            # 3. Session会话
    'CommonMiddleware',             # 4. 通用处理（APPEND_SLASH、ETag）
    'CsrfViewMiddleware',           # 5. CSRF保护（API用JWT替代）
    'AuthenticationMiddleware',     # 6. 用户认证（request.user注入）
    'MessageMiddleware',            # 7. 消息框架
    'XFrameOptionsMiddleware',      # 8. 点击劫持防护
    'ExceptionMiddleware',          # 9. ★ 全局异常捕获（统一JSON响应）
    'LoggingMiddleware',            # 10. ★ 请求日志记录
    'ApiStatsMiddleware',           # 11. ★ API调用统计（响应时间计数）
]
```

#### 2.2.3 模型继承体系

所有业务模型统一继承 `BaseModel`，自动获得：

```python
class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    TimeStampedModel:
      - created_at: DateTimeField(auto_now_add)  创建时间
      - updated_at: DateTimeField(auto_now)       更新时间

    SoftDeleteModel:
      - is_deleted: BooleanField(default=False)   软删除标记
      - deleted_at: DateTimeField(null)           删除时间
      - deleted_by: ForeignKey(User)              删除操作人
      - soft_delete(user) / restore()             软删除/恢复方法
    """
    pass
```

此外还有 `SingletonModel`（单例模型，如SystemSetting）和 `SystemOperationLog`（审计日志，含模块/操作类型/IP/Request-ID全链路追踪）。

### 2.3 缓存架构深度解析（★核心技术）

本项目实现了一套**企业级多层缓存管理体系**，是性能优化的核心组件。

#### 2.3.1 缓存键命名规范

```
前缀规则: lims:{domain}:{entity}:{identifier}

示例键:
  lims:statistics:dashboard:3            → 用户3的仪表盘数据
  lims:statistics:comprehensive:3:5      → 用户5在学期3的综合统计
  lims:laboratory:options:3              → 用户3可见的实训室选项列表
  lims:user:permissions:7                → 用户7的权限缓存
  lims:semester:current                  → 当前活跃学期
  api:schedule:list:*                    → API层课表列表缓存（通配符模式）
```

#### 2.3.2 缓存失效策略

采用**事件驱动型缓存失效**，通过装饰器模式自动关联：

| 失效触发器 | 清理目标缓存域 |
|-----------|--------------|
| 课表增删改 | `schedule:list:*` + `statistics:dashboard/comprehensive:*` |
| 实训室变更 | `lab:list:*` + `laboratory:options:*` + 统计缓存 |
| 设备变更 | `equipment:list:*` + `equipment:options:*` + 统计缓存 |
| 用户变更 | `user:list:*` + `user:permissions/info:*` + 统计缓存 |
| 工单变更 | `workorder:list:*` + 统计缓存 |
| 记录变更 | `record:list:*` + 统计缓存 |
| 学期切换 | `semester:*` + 全部 `statistics:*` |

**事务安全机制**：通过 `CacheContext` 上下文管理器确保数据库事务回滚时缓存不会脏写：

```python
with CacheContext():                          # 进入事务模式
    with transaction.atomic():
        schedule.delete()
        CacheInvalidator.invalidate_schedule_cache()  # 加入待清理队列
    # 事务成功 → flush_pending() 执行清理
    # 事务失败 → clear_pending() 放弃清理
```

---

## 三、frontend — Vue 3 双端前端深度解析

### 3.1 双构建配置技术差异

项目维护**两套独立的Vite配置文件**，针对PC和移动端分别优化：

| 配置项 | PC端 ([vite.config.pc.js](frontend/vite.config.pc.js)) | 移动端 ([vite.config.mobile.js](frontend/vite.config.mobile.js)) |
|--------|------------------------------------------------------|---------------------------------------------------------------|
| 入口HTML | `index.pc.html` | `index.mobile.html` |
| 开发端口 | **5173** | **5174** |
| UI Resolver | **ElementPlusResolver**(importStyle=css, locale=zh-cn) | **VantResolver** |
| 输出目录 | `dist/pc/` | `dist/mobile/` |
| 代码分割 | element-plus / vue-vendor / axios / echarts(含vue-echarts) | vant / vue-vendor / axios |
| Base路径 | `./`（相对路径） | `/`（绝对根路径） |

**共享配置**：
- **AutoImport**: 自动导入 `vue` 和 `vue-router` 的API（ref/reactive/onMounted等），无需手动import
- **Components**: UI组件按需自动引入（unplugin-vue-components），减小包体积
- **Terser压缩**: 生产构建移除console和debugger语句
- **Proxy代理**: 开发模式下 `/api` → `http://127.0.0.1:8000`，`/ws` → WebSocket代理

### 3.2 高并发请求架构（★核心技术）

前端实现了**生产级的HTTP请求管控体系**，由三个协同模块构成：

#### 3.2.1 RequestQueue — 并发控制队列

```
核心参数:
  maxConcurrent = 6          最大并发请求数
  dedupeWindow = 500ms       请求去重时间窗口
  retryTimes = 2             自动重试次数
  retryDelay = 1000ms        重试间隔

工作机制:
  1. 请求进入 → 生成唯一Key（method:url:params:data排序序列化）
  2. 去重检查 → 窗口内相同请求返回已有Promise或拒绝
  3. 并发控制 → activeCount < maxConcurrent 时立即执行，否则入队等待
  4. AbortController → 每个请求绑定取消控制器，支持单个/批量取消
  5. 自动重试 → 仅对网络错误(ECONNABORTED/ERR_NETWORK)和服务端错误(5xx)重试
  6. 完成回调 → activeCount-- → 触发process()消费队列中的下一个任务
```

#### 3.2.2 RequestCache — LRU内存缓存

```
核心参数:
  defaultTTL = 60秒          默认缓存有效期
  maxSize = 100条            最大缓存条目数
  cleanupInterval = 60秒     定时清理过期缓存

数据结构:
  cache: Map<key, CacheItem>     O(1)查找
  accessOrder: string[]          LRU访问顺序链表

淘汰策略:
  1. 写入时超容 → evict()淘汰最久未访问的条目
  2. 读取命中 → 移至accessOrder末尾（最新）
  3. 定时任务 → cleanup()清除过期条目

特殊逻辑:
  - 统计类API（dashboard/stats/analytics）→ 强制禁用缓存（实时性优先）
  - POST/PUT/PATCH/DELETE成功后 → 自动clearPattern清除相关GET缓存
```

#### 3.2.3 Axios Client — 拦截器管道

```
请求拦截器链:
  ① 注入JWT Token → Authorization: Bearer xxx
  ② URL规范化 → 补全前导斜杠
  ③ GET缓存检查 → 命中则直接返回_cachedData（短路）
  ④ 重复请求检测 → pendingRequests Map去重

响应拦截器链:
  ① 缓存命中返回 → _fromCache标记直接返回缓存数据
  ② 清理去重Map → 删除_requestKey
  ③ 文件下载透传 → blob类型不处理
  ④ GET结果写入缓存 → defaultCache.set()
  ⑤ 写操作缓存失效 → clearPattern清除相关资源缓存
  ⑥ 401处理 → 清除Token → 跳转登录页
```

### 3.3 状态管理与路由架构

**Pinia Store**（三个核心Store）：
- `user.js` — 用户身份、Token、权限列表、部门信息
- `app.js` — 应用全局状态（当前学期、侧栏折叠、主题）
- `index.js` — Store注册中心

**路由设计**：
- PC端路由 (`router/index.js`) — 懒加载 + 路由守卫（auth验证 + 权限meta）
- Mobile端路由 (`router/mobile.js`) — TabBar页面 + 嵌套路由（详情页）
- 路由决策器 (`utils/routeDecision.js`) — 根据角色动态生成可访问路由表

### 4 Hooks体系（组合式函数）

```
core/hooks/
├── base/                         # 基础能力Hook
│   ├── useApi.js                 # API调用封装（集成队列+缓存+错误处理）
│   ├── useCRUD.js                # CRUD标准操作模板（create/read/update/delete）
│   ├── useBaseList.js            # 列表页逻辑（分页/排序/筛选/搜索）
│   ├── useForm.js                # 表单状态管理（校验/提交/重置）
│   ├── useEntityForm.js          # 实体表单（关联字段联动）
│   ├── useDelete.js              # 删除确认+执行+列表刷新
│   └── useAutoRefresh.js         # 定时自动刷新（仪表盘场景）
│
├── domain/                       # 领域业务Hook
│   ├── useClassList.js           # 班级管理
│   ├── useDeptList.js            # 部门管理（树形）
│   ├── useUserList.js            # 用户管理（角色筛选）
│   ├── useRecordList.js          # 使用记录（日期范围）
│   ├── useSxsList.js             # 学期/归档管理
│   ├── useMaintainList.js        # 维护工单列表
│   ├── useDashboardCharts.js     # 图表数据组装
│   └── ...
│
└── mobile/                       # 移动端专用Hook
    ├── useMobileList.js          # 移动端列表（上拉加载/下拉刷新）
    └── useMobileForm.js          # 移动端表单（底部弹出/键盘适配）
```

---

## 四、tauri-mobile — Tauri Android 原生应用

### 4.1 技术架构

```
┌─────────────────────────────────────────┐
│         Android 应用层 (Kotlin)          │
│  build.gradle.kts (compileSdk=36)       │
│  minSdk=24 / targetSdk=36               │
│  package: com.lims.mobile               │
│  WebView (androidx.webkit:1.14)         │
├─────────────────────────────────────────┤
│         Tauri 运行时 (Rust)              │
│  Cargo.toml (edition=2021)              │
│  tauri = "2"                            │
│  tauri-plugin-shell = "2"               │
│  serde + serde_json (序列化)             │
│  lib.rs → Builder::default().run()      │
├─────────────────────────────────────────┤
│         前端资源 (Vue + Vant)            │
│  vite.config.js (port=1420)             │
│  src/views/mobile/ (复用移动端页面)      │
│  main.mobile.js (移动端入口)             │
└─────────────────────────────────────────┘
```

### 4.2 构建配置要点

**Tauri配置** ([tauri.conf.json](tauri-mobile/src-tauri/tauri.conf.json))：
- 产品名称: `LIMS 实验室管理系统`
- 标识符: `com.lims.mobile`
- 默认窗口: 414×896（iPhone 11尺寸基准）
- 开发服务器: `http://localhost:1420`
- CSP: null（开发模式放宽限制）

**Rust依赖** ([Cargo.toml](tauri-mobile/src-tauri/Cargo.toml))：
- `tauri` v2 — 核心运行时
- `tauri-plugin-shell` v2 — Shell命令执行插件
- `serde` + `serde_json` — JSON序列化/反序列化
- 条件编译: 非Android/iOS平台才加载shell插件

**Android Gradle配置** ([build.gradle.kts](tauri-mobile/src-tauri/gen/android/app/build.gradle.kts))：
- Kotlin JVM Target: 1.8
- Debug签名: `~/.android/debug.keystore`（标准Android调试证书）
- Release: 启用ProGuard混淆 + Minify
- JNI支持: arm64-v8a / armeabi-v7a / x86 / x86_64 四架构
- 依赖: AppCompat + Material Design + WebKit

### 4.3 与Web端的差异

| 特性 | Web移动端 | Tauri Android |
|------|----------|---------------|
| 运行环境 | 浏览器WebView | 系统WebView（更底层控制） |
| 离线支持 | 依赖ServiceWorker | 资源内置APK，天然离线可用 |
| 原生能力 | 受限（需PWA） | 可通过Rust调用原生API |
| 分发方式 | 访问URL | APK安装/GPlay上架 |
| 启动速度 | 取决于网络 | 本地资源秒开 |
| 更新机制 | 自动（服务端部署） | 需重新打包发布APK |

---

## 五、Nginx 网关配置技术细节

### 5.1 路由分发规则

```nginx
# 1. 根路径设备检测（UA正则匹配30+种移动设备标识）
location = / {
    if ($http_user_agent ~* "(android|iphone|mobile|...)")
        → return 301 /m/;
    → root /pc; index index.pc.html;
}

# 2. 移动端别名映射
location /m/ {
    alias /usr/share/nginx/mobile/;
    try_files $uri $uri/ /m/index.mobile.html;  # SPA fallback
    Cache-Control: no-cache;  # HTML始终新鲜
}

# 3. API反向代理（upstream: backend容器）
location /api/ {
    proxy_pass http://backend;
    proxy_http_version 1.1;           # HTTP/1.1 Keep-Alive
    proxy_set_header Connection "";   # 连接池复用
    buffer_size: 4k; buffers: 8×32k; # 响应缓冲调优
    timeout: connect=60s send=120s read=120s;
    next_upstream: error timeout 502/503/504 (最多3次);
}

# 4. WebSocket升级代理
location /ws/ {
    proxy_pass http://backend;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout: 86400s (24h长连接);
}

# 5. 静态资源长期缓存
location /assets/ { expires 1y; Cache-Control: public immutable; }
location /static/ { expires 30d; Cache-Control: public immutable; }
location /media/  { expires 7d;  Cache-Control: public; }

# 6. 健康检查端点
location /health { return 200 "healthy\n"; access_log off; }

# 7. PC SPA fallback
location / { try_files $uri $uri/ /index.pc.html; }
```

### 5.2 性能优化策略

- **Gzip压缩**: nginx.conf中开启gzip on，压缩text/css/application/javascript/application/json
- **连接池**: upstream keepalive复用到后端的TCP连接
- **缓冲优化**: 减少磁盘I/O，proxy_buffering on
- **缓存层次**: HTML(no-cache) < Media(7d) < Static(30d) < Assets(1y immutable)

---

## 六、Docker Compose 编排详解

### 6.1 服务依赖与健康检查

```
启动顺序（depends_on + condition）:

  Phase 1: 基础设施层（无依赖，并行启动）
    ├── redis:7-alpine     → healthcheck: redis-cli ping (interval=5s, retries=10)
    └── mysql:8.0          → healthcheck: mysqladmin ping (interval=5s, retries=20, start_period=30s)

  Phase 2: 应用层（依赖Phase 1健康）
    └── backend:Django     → depends_on: db(healthy) + redis(healthy)
                            → healthcheck: urllib访问 /api/v1/common/health/ (retries=30)

  Phase 3: 构建层（无健康检查，started即可）
    ├── frontend-pc        → build context: ./frontend (Dockerfile.pc)
    └── frontend-mobile    → build context: ./frontend (Dockerfile.mobile)

  Phase 4: 网关层（依赖Phase 2+3）
    └── nginx              → depends_on: backend(healthy) + frontend-pc(started) + mobile(started)
```

### 6.2 数据卷持久化

| 卷名 | 用途 | 宿主机映射 |
|------|------|-----------|
| `db_data` | MySQL数据持久化 | Docker managed volume |
| `redis_data` | Redis AOF/RDB持久化 | Docker managed volume |
| `static_volume` | Django collectstatic产物 | 共享给nginx容器 |
| `pc_dist` | PC端构建产物 | 共享给nginx:/usr/share/nginx/html/pc |
| `mobile_dist` | Mobile端构建产物 | 共享给nginx:/usr/share/nginx/html/mobile |

### 6.3 网络拓扑

```
lims_network (bridge驱动)
  所有容器位于同一桥接网络，通过容器名DNS互相发现
  backend连接 db:3306 和 redis:6379（内部端口，不暴露宿主机）
  仅nginx和backend暴露端口至宿主机
```

---

## 七、操作时限参考手册

### 7.1 开发环境搭建

| 步骤 | 操作命令 | 预计耗时 | 说明 |
|------|---------|---------|------|
| 1 | 安装 Node.js ≥20.19 + Python ≥3.10 + MySQL 8 + Redis 7 | 15-30min | 首次环境准备 |
| 2 | `cd backend-v2 && python -m venv venv && source venv/bin/activate` | 30s | 创建虚拟环境 |
| 3 | `pip install -r requirements/development.txt` | 3-5min | 下载Python依赖 |
| 4 | `cp .env.example .env && 编辑配置` | 2-3min | 数据库/Redis/JWT密钥 |
| 5 | `python manage.py migrate` | 30s-2min | 建表（11个App约40张表） |
| 6 | `python manage.py createsuperuser` | 1min | 创建管理员账号 |
| 7 | `cd ../frontend && npm install` | 2-4min | 下载Node依赖（含Element+/Vant/ECharts） |
| 8 | `npm run dev:pc` (终端1) | <10s | PC端 dev server :5173 |
| 9 | `npm run dev:mobile` (终端2) | <10s | Mobile dev server :5174 |
| 10 | `cd ../backend-v2 && python manage.py runserver` (终端3) | <5s | Django dev server :8000 |
| **总计** | | **~25-45min** | **首次完整搭建** |

### 7.2 生产环境Docker部署

| 步骤 | 操作 | 预计耗时 | 说明 |
|------|------|---------|------|
| 1 | 安装Docker Desktop | 5-10min | 下载安装 |
| 2 | `copy .env.example .env` + 编辑必填项 | 3-5min | SECRET_KEY/DB_PASSWORD等6项必填 |
| 3 | `deploy.bat` 或 `./deploy.sh` | 20-30min | 一键构建+启动全部6个容器 |
| 4 | 验证 `docker-compose ps` | 10s | 确认全部healthy |
| 5 | 浏览器访问 http://localhost | 即时 | PC端自动呈现 |
| **总计** | | **~30-45min** | **含首次镜像拉取** |

后续更新仅需 `docker-compose up -d --build`，增量构建 **3-8min**。

### 7.3 Tauri Android 打包

| 步骤 | 操作 | 预计耗时 | 说明 |
|------|------|---------|------|
| 1 | 安装 Rust (rustup) | 10-20min | 下载rustup-init |
| 2 | 安装 Android SDK/NDK/Build Tools/CMake | 15-30min | 通过Android Studio SDK Manager |
| 3 | 配置 ANDROID_HOME + PATH | 2min | 环境变量设置 |
| 4 | `cd tauri-mobile && yarn install` | 3-5min | Node依赖 |
| 5 | `yarn tauri android build --release` | 10-25min | Rust编译+Gradle构建+APK签名 |
| **总计** | | **~30-80min** | **取决于机器性能和网络** |

### 7.4 日常运维操作

| 操作 | 命令 | 耗时 |
|------|------|------|
| 查看日志 | `docker-compose logs -f backend` | 即时 |
| 重启服务 | `docker-compose restart nginx` | 5-10s |
| 数据库备份 | `docker exec lims_db mysqldump ... > backup.sql` | 1-3min |
| 数据库恢复 | `docker exec -i lims_db mysql ... < backup.sql` | 2-5min |
| 清理缓存 | `docker exec lims_backend python manage.py shell` → CacheManager | <1s |
| 静态文件更新 | `docker exec lims_backend python manage.py collectstatic` | 10-30s |
| 后端测试 | `cd backend-v2 && pytest` | 3-5min |
| 前端PC构建 | `cd frontend && npm run build:pc` | 1-2min |
| 前端Mobile构建 | `cd frontend && npm run build:mobile` | 1-2min |

---

## 八、安全架构总结

| 安全层面 | 技术措施 | 实现位置 |
|---------|---------|---------|
| **传输加密** | HTTPS/TLS 1.3 | Nginx SSL配置 |
| **身份认证** | JWT Access+Refresh Token轮换 | DRF SimpleJWT |
| **密码安全** | 前端AES加密 + 后端bcrypt哈希 | CryptoJS + Django |
| **授权控制** | RBAC角色权限 + 接口级别Permission | DRF Permission类 |
| **CSRF防护** | API用JWT替代Session Cookie | 中间件配置 |
| **CORS限制** | 白名单Origin控制 | django-cors-headers |
| **SQL注入防护** | Django ORM参数化查询 | ORM层自动防护 |
| **XSS防护** | Django模板自动转义 + Content-Security-Policy | SecurityMiddleware |
| **审计追踪** | SystemOperationLog全量记录 | core.models |
| **软删除** | 数据标记删除非物理删除 | SoftDeleteModel |
| **敏感信息** | .env环境变量管理 | docker-compose env_file |
| **Rate Limiting** | 前端请求队列并发控制(6) | RequestQueue |
| **API文档安全** | SERVE_INCLUDE_SCHEMA=False（生产关闭） | drf-spectacular |

---

## 九、扩展性与可维护性设计

### 9.1 新增业务模块的标准步骤

1. `apps/` 下创建新目录（models/services/serializers/views/urls/apps.py 五件套）
2. 在 `INSTALLED_APPS` 注册
3. 在 `api/v1/urls.py` include路由
4. 在 `CacheInvalidator` 新增对应缓存失效方法
5. 前端 `views/pc/crud/` + `views/mobile/crud/` 创建页面
6. 前端 `hooks/domain/` 创建useXxxList Hook
7. 前端 `router/` 注册路由 + meta权限标记
8. Dockerfile无需改动（动态发现）

### 9.2 配置外置化

所有环境相关配置均通过环境变量/Docker环境注入，无硬编码：
- 数据库连接 → DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD
- Redis → REDIS_URL
- 密钥 → SECRET_KEY / PASSWORD_ENCRYPT_KEY
- AI → DEEPSEEK_API_KEY / DEEPSEEK_SERVICE_URL / DEEPSEEK_MODEL
- 部署 → ALLOWED_HOSTS / SERVER_PORT / CORS_ALLOWED_ORIGINS

### 9.3 多环境无缝切换

```bash
development → DJANGO_ENV=development  → settings/development.py
testing     → DJANGO_ENV=testing      → settings/testing.py (SQLite内存)
production  → DJANGO_ENV=production   → settings/production.py (安全加固)
```

---

> **文档维护说明**: 本文档随项目迭代同步更新。涉及技术架构变更时，请同步修订对应章节。
>
> **快速定位索引**: backend-v2(Django API) | frontend(Vue双端) | tauri-mobile(Android原生) | nginx(网关) | docker-compose(编排)
