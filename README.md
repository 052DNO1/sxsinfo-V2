# 实训室信息管理系统 (LIMS)

一个基于 Vue 3 + Django 的实训室信息管理系统，支持 PC 端和移动端双端访问。

## 功能特性

- **实训室管理**：实训室信息增删改查、工位管理、管理员分配
- **课表管理**：课程排课、周次节次管理、教师关联、冲突检测
- **使用记录**：实训室使用情况记录、教师签名、设备状态
- **维护管理**：工单系统、工单中心、维护申请、维护记录、维护类型分类
- **设备管理**：设备信息录入、状态跟踪、位置管理
- **用户管理**：多角色用户、部门管理、权限分配
- **学期管理**：学期设置、数据归档
- **数据导入导出**：Excel 批量导入导出
- **统计报表**：使用统计、综合数据展示、多维度仪表盘（实训室资源、设备管理、个人教学、用户管理）
- **AI 助手**：集成 DeepSeek AI 智能助手
- **通知系统**：消息通知、工单提醒
- **备份恢复**：自动备份、数据恢复
- **缓存管理**：缓存配置查看与管理
- **全局搜索**：全站数据快速检索
- **操作日志**：用户操作记录与审计
- **双端适配**：统一前端项目，PC 端使用 Element Plus，移动端使用 Vant

## 技术栈

### 前端

| 技术                      | 版本     | 说明                |
| ----------------------- | ------ | ----------------- |
| Vue                     | 3.5.x  | 渐进式 JavaScript 框架 |
| Vite                    | 7.x    | 下一代前端构建工具         |
| Vue Router              | 4.x    | 官方路由管理器           |
| Pinia                   | 3.x    | Vue 状态管理库         |
| Element Plus            | 2.x    | PC 端 UI 组件库       |
| Vant                    | 4.x    | 移动端 UI 组件库        |
| ECharts                 | 5.x    | 数据可视化图表库          |
| vue-echarts             | 6.x    | ECharts Vue 组件封装  |
| Axios                   | 1.x    | HTTP 请求库          |
| xlsx                    | 0.18.x | Excel 文件处理        |
| FlexSearch              | 0.8.x  | 全文搜索引擎            |
| CryptoJS                | 4.x    | 加密库               |
| unplugin-auto-import    | 20.x   | 自动导入插件            |
| unplugin-vue-components | 30.x   | 组件自动注册插件          |

### 后端

| 技术                    | 版本     | 说明             |
| --------------------- | ------ | -------------- |
| Django                | 4.2.x  | Python Web 框架  |
| Django REST Framework | 3.14.x | RESTful API 框架 |
| SimpleJWT             | 5.3.x  | JWT 认证         |
| django-cors-headers   | 4.3.x  | CORS 跨域支持      |
| django-filter         | 23.5.x | 查询过滤器          |
| django-redis          | 5.4.x  | Redis 缓存后端     |
| django-mptt           | 0.16.x | 树形结构支持         |
| drf-spectacular       | 0.27.x | API 文档生成       |
| MySQL                 | 8.0    | 关系型数据库         |
| Redis                 | 7.x    | 缓存服务           |
| Celery                | 5.3.x  | 异步任务队列         |
| Gunicorn              | 21.x   | WSGI 服务器       |
| Gevent                | 23.9.x | 协程库            |
| openpyxl              | 3.1.x  | Excel 文件读写     |
| pandas                | 2.x    | 数据分析处理         |
| pycryptodome          | 3.19.x | 密码加密库          |
| reportlab             | 4.x    | PDF 生成         |

## 项目结构

```
V2/
├── frontend/                    # 统一前端项目 (PC端 + 移动端)
│   ├── src/
│   │   ├── assets/              # 静态资源
│   │   │   └── css/             # 样式文件 (含移动端样式)
│   │   ├── components/          # 公共组件
│   │   ├── core/                # 核心 JS 模块
│   │   │   ├── api/             # API 客户端、请求队列
│   │   │   ├── auth/            # 认证模块
│   │   │   ├── config/          # 配置文件 (实体字段、图标、导入配置、列表配置)
│   │   │   ├── hooks/           # 组合式函数
│   │   │   │   ├── base/        # 基础 hooks (CRUD、表单、列表、API)
│   │   │   │   ├── domain/      # 业务 hooks (课表、记录、用户等)
│   │   │   │   └── mobile/      # 移动端 hooks
│   │   │   ├── router/          # 路由配置 (PC端 + 移动端)
│   │   │   ├── services/        # 服务层
│   │   │   ├── store/           # Pinia 状态管理
│   │   │   └── utils/           # 工具函数
│   │   ├── views/
│   │   │   ├── pc/              # PC 端页面
│   │   │   │   ├── auth/        # 认证页面
│   │   │   │   ├── common/      # 公共页面 (AI助手、全局搜索、消息、工单中心)
│   │   │   │   ├── components/  # 业务组件 (布局、数据表格、课表网格等)
│   │   │   │   ├── crud/        # CRUD 页面
│   │   │   │   ├── dashboard/   # 仪表盘 (综合、实训室资源、设备、个人教学、用户管理)
│   │   │   │   ├── lab/         # 实训室管理 (归档、导入、设备)
│   │   │   │   ├── stats/       # 统计页面
│   │   │   │   ├── system/      # 系统管理 (备份、缓存配置、操作日志)
│   │   │   │   └── user/        # 用户管理
│   │   │   └── mobile/          # 移动端页面
│   │   │       ├── auth/        # 认证页面
│   │   │       ├── common/      # 公共页面
│   │   │       ├── components/  # 移动端组件 (布局、TabBar)
│   │   │       ├── crud/        # CRUD 页面
│   │   │       ├── dashboard/   # 仪表盘 + 工具箱
│   │   │       ├── lab/         # 实训室管理
│   │   │       ├── system/      # 系统管理
│   │   │       └── user/        # 用户管理
│   │   ├── App.vue
│   │   ├── main.js              # PC 端入口
│   │   └── main.mobile.js       # 移动端入口
│   ├── vite.config.pc.js        # PC 端 Vite 配置
│   ├── vite.config.mobile.js    # 移动端 Vite 配置
│   ├── index.pc.html            # PC 端 HTML 模板
│   ├── index.mobile.html        # 移动端 HTML 模板
│   ├── Dockerfile.pc            # PC 端 Docker 构建
│   ├── Dockerfile.mobile        # 移动端 Docker 构建
│   └── package.json
│
├── backend-v2/                  # 后端项目
│   ├── apps/                    # 应用模块
│   │   ├── core/                # 核心基础模块 (操作日志、异常处理、中间件)
│   │   ├── users/               # 用户管理 (认证、部门、系统设置)
│   │   ├── laboratories/        # 实训室管理 (实训室、设备)
│   │   ├── schedules/           # 课表管理 (排课、学期、归档)
│   │   ├── records/             # 使用记录
│   │   ├── maintenance/         # 维护/工单管理 (工单、工单中心)
│   │   ├── notifications/       # 通知模块
│   │   ├── ai_assistant/        # AI 助手
│   │   ├── backup/              # 备份恢复
│   │   ├── cache_config/        # 缓存配置管理
│   │   └── statistics/          # 统计分析
│   ├── common/                  # 公共模块
│   │   ├── services/            # 公共服务 (缓存、导入导出、进度、搜索)
│   │   ├── utils/               # 公共工具 (加密)
│   │   ├── views/               # 公共视图 (健康检查、导入导出、进度、搜索)
│   │   ├── decorators.py        # 装饰器
│   │   ├── enums.py             # 枚举定义
│   │   ├── filters.py           # 过滤器
│   │   ├── mixins.py            # 视图混入
│   │   ├── paginations.py       # 分页配置
│   │   ├── responses.py         # 统一响应格式
│   │   └── validators.py        # 验证器
│   ├── extensions/              # 扩展模块
│   │   ├── celery_app.py        # Celery 配置
│   │   └── redis_client.py      # Redis 客户端
│   ├── api/                     # API 路由
│   │   └── v1/                  # V1 版本路由
│   ├── lims/                    # 项目配置
│   │   ├── settings/            # 多环境配置 (base/development/production/testing)
│   │   ├── urls.py              # 主路由
│   │   ├── asgi.py              # ASGI 配置
│   │   └── wsgi.py              # WSGI 配置
│   ├── tests/                   # 测试
│   │   ├── unit/                # 单元测试
│   │   ├── integration/         # 集成测试
│   │   ├── e2e/                 # 端到端测试
│   │   ├── blackbox/            # 黑盒测试
│   │   └── whitebox/            # 白盒测试
│   ├── scripts/                 # 脚本工具
│   ├── utils/                   # 工具函数
│   ├── requirements/            # 依赖配置
│   │   ├── base.txt             # 基础依赖
│   │   ├── development.txt      # 开发环境
│   │   ├── production.txt       # 生产环境
│   │   └── testing.txt          # 测试环境
│   ├── pyproject.toml           # Python 项目配置
│   ├── pytest.ini               # 测试配置
│   ├── Dockerfile               # Docker 构建
│   ├── entrypoint.sh            # 容器入口脚本
│   └── manage.py
│
├── nginx/                       # Nginx 配置
│   ├── nginx.conf               # Nginx 主配置
│   └── conf.d/                  # 站点配置
│       └── default.conf
├── docker-compose.yml           # Docker 编排
├── .env.example                 # 环境变量示例
├── deploy.sh                    # Linux 部署脚本
├── deploy.bat                   # Windows 部署脚本
├── DEPLOY.md                    # 部署文档
├── DEPLOY_LINUX.md              # Linux 部署文档
└── TECHNICAL_GUIDE.md           # 技术指南
```

## 快速开始

### 环境要求

- Node.js ^20.19.0 || >=22.12.0
- Python >= 3.10
- MySQL >= 8.0
- Redis >= 7.0

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# PC 端开发模式
npm run dev:pc

# 移动端开发模式
npm run dev:mobile

# PC 端生产构建
npm run build:pc

# 移动端生产构建
npm run build:mobile

# PC 端预览
npm run preview:pc

# 移动端预览
npm run preview:mobile

# 代码检查
npm run lint
```

### 后端启动

```bash
cd backend-v2

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements/development.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库、Redis 等

# 数据库迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

### 环境变量配置

后端需要在 `.env` 文件或环境变量中配置：

```bash
# Django 配置
SECRET_KEY=your-secret-key
DJANGO_ENV=development
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173

# 数据库配置
DB_NAME=lims
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# AI 助手配置 (可选)
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_SERVICE_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat

# 密码加密密钥 (前后端必须一致)
PASSWORD_ENCRYPT_KEY=your-encrypt-key
```

## 核心数据模型

### 实训室

- 实训室名称、门牌号、工位数
- 管理员、所属部门
- 状态、备注

### 课表

- 课程名称、星期、节次、周次
- 上课班级、任课教师
- 关联实训室、学期

### 使用记录

- 使用日期、节次、学时
- 使用人数、实训内容
- 设备状态、教师签名

### 工单

- 工单编号、维护类型
- 维护内容、维护人员
- 请求时间、完成时间、状态

### 设备

- 设备编号、名称、品牌、型号
- CPU、内存、硬盘配置
- 位置、状态

### 通知

- 通知类型、标题、内容
- 发送者、接收者
- 已读状态

### 缓存配置

- 缓存键、分类
- 超时时间、描述

## API 文档

启动后端服务后访问：

- Swagger UI: <http://localhost:8000/api/docs/>
- ReDoc: <http://localhost:8000/api/redoc/>

## 用户角色

| 角色          | 权限         |
| ----------- | ---------- |
| 超级管理员-系统管理员 | 全部权限       |
| 管理员-校长      | 用户管理、系统配置  |
| 实训室管理员      | 实训室管理、设备管理 |
| 教师          | 使用记录、维护申请  |
| 普通用户        | 查看权限       |

## 部署说明

### Docker 部署

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件（必须配置 SECRET_KEY、DB_PASSWORD、DB_ROOT_PASSWORD 等）

# 一键部署 (Linux)
chmod +x deploy.sh && ./deploy.sh

# 一键部署 (Windows)
deploy.bat

# 或手动启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 生产环境

1. 使用 Gunicorn + Gevent 作为 WSGI 服务器
2. 使用 Nginx 反向代理静态资源，分别服务 PC 端和移动端
3. 配置 HTTPS 证书
4. 配置 Redis 缓存
5. 配置 Celery 异步任务
6. 前后端密码加密密钥必须一致

## 开发规范

### 前端

- 使用 Composition API 编写组件
- 使用 Pinia 管理全局状态
- 使用 hooks 封装可复用逻辑（base / domain / mobile 三层结构）
- 使用 unplugin-auto-import 和 unplugin-vue-components 自动导入
- PC 端和移动端共享 core 模块，各自独立视图和路由
- 遵循 Vue 3 风格指南

### 后端

- 使用 Django REST Framework 构建 API
- 使用 Services 层封装业务逻辑
- 使用 Serializers 处理数据序列化
- 使用 Celery 处理异步任务
- 使用 common 模块提供统一响应、分页、过滤、验证等基础设施
- 遵循 Django 最佳实践

## 测试

```bash
cd backend-v2

# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行端到端测试
pytest tests/e2e/

# 运行黑盒测试
pytest tests/blackbox/

# 运行白盒测试
pytest tests/whitebox/

# 生成覆盖率报告
pytest --cov=apps
```

## 作者

LIMS Team
