# 实训室信息管理系统 (LIMS)

一个基于 Vue 3 + Django 的实训室信息管理系统，支持 PC 端和移动端双端访问。

## 功能特性

- **实训室管理**：实训室信息增删改查、工位管理、管理员分配
- **课表管理**：课程排课、周次节次管理、教师关联、冲突检测
- **使用记录**：实训室使用情况记录、教师签名、设备状态
- **维护管理**：工单系统、维护申请、维护记录、维护类型分类
- **设备管理**：设备信息录入、状态跟踪、位置管理
- **用户管理**：多角色用户、部门管理、权限分配
- **学期管理**：学期设置、数据归档
- **数据导入导出**：Excel 批量导入导出
- **统计报表**：使用统计、综合数据展示、多维度仪表盘
- **AI 助手**：集成 DeepSeek AI 智能助手
- **通知系统**：消息通知、工单提醒
- **备份恢复**：自动备份、数据恢复
- **双端适配**：自动识别设备，PC 端使用 Element Plus，移动端使用 Vant

## 技术栈

### 前端 (PC)

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.5.x | 渐进式 JavaScript 框架 |
| Vite | 7.x | 下一代前端构建工具 |
| Vue Router | 4.x | 官方路由管理器 |
| Pinia | 3.x | Vue 状态管理库 |
| Element Plus | 2.x | PC 端 UI 组件库 |
| ECharts | 5.x | 数据可视化图表库 |
| Axios | 1.x | HTTP 请求库 |
| xlsx | 0.18.x | Excel 文件处理 |
| FlexSearch | 0.8.x | 全文搜索引擎 |
| CryptoJS | 4.x | 加密库 |

### 后端

| 技术 | 版本 | 说明 |
|------|------|------|
| Django | 4.2.x | Python Web 框架 |
| Django REST Framework | 3.14.x | RESTful API 框架 |
| SimpleJWT | 5.3.x | JWT 认证 |
| MySQL | 8.0 | 关系型数据库 |
| Redis | 7.x | 缓存服务 |
| Celery | 5.3.x | 异步任务队列 |
| Gunicorn | 21.x | WSGI 服务器 |
| drf-spectacular | 0.27.x | API 文档生成 |
| django-mptt | 0.16.x | 树形结构支持 |

## 项目结构

```
V2/
├── pc/                          # PC 端前端项目
│   ├── src/
│   │   ├── assets/              # 静态资源
│   │   ├── components/          # 公共组件
│   │   ├── core/                # 核心 JS 模块
│   │   │   ├── api/             # API 客户端
│   │   │   ├── auth/            # 认证模块
│   │   │   ├── config/          # 配置文件
│   │   │   ├── hooks/           # 组合式函数
│   │   │   ├── router/          # 路由配置
│   │   │   ├── services/        # 服务层
│   │   │   ├── store/           # Pinia 状态管理
│   │   │   └── utils/           # 工具函数
│   │   ├── core-ts/             # TypeScript 核心 (迁移中)
│   │   └── views/               # 页面组件
│   │       └── pc/
│   │           ├── auth/        # 认证页面
│   │           ├── common/      # 公共页面
│   │           ├── components/  # 业务组件
│   │           ├── crud/        # CRUD 页面
│   │           ├── dashboard/   # 仪表盘
│   │           ├── lab/         # 实训室管理
│   │           ├── stats/       # 统计页面
│   │           ├── system/      # 系统管理
│   │           └── user/        # 用户管理
│   ├── public/                  # 公共资源
│   └── package.json
│
├── backend-v2/                  # 后端项目
│   ├── apps/                    # 应用模块
│   │   ├── core/                # 核心基础模块
│   │   ├── users/               # 用户管理
│   │   ├── laboratories/        # 实训室管理
│   │   ├── schedules/           # 课表管理
│   │   ├── records/             # 使用记录
│   │   ├── maintenance/         # 维护/工单管理
│   │   ├── notifications/       # 通知模块
│   │   ├── ai_assistant/        # AI 助手
│   │   ├── backup/              # 备份恢复
│   │   └── statistics/          # 统计分析
│   ├── common/                  # 公共模块
│   │   ├── services/            # 公共服务
│   │   └── views/               # 公共视图
│   ├── extensions/              # 扩展模块
│   │   ├── celery_app.py        # Celery 配置
│   │   └── redis_client.py      # Redis 客户端
│   ├── api/                     # API 路由
│   ├── lims/                    # 项目配置
│   │   ├── settings/            # 多环境配置
│   │   └── urls.py              # 主路由
│   ├── tests/                   # 测试
│   │   ├── unit/                # 单元测试
│   │   ├── integration/         # 集成测试
│   │   └── e2e/                 # 端到端测试
│   ├── scripts/                 # 脚本工具
│   ├── requirements/            # 依赖配置
│   └── manage.py
│
├── docker-compose.yml           # Docker 编排
├── nginx.conf                   # Nginx 配置
└── generate_keys.py             # 密钥生成工具
```

## 快速开始

### 环境要求

- Node.js >= 20.19.0
- Python >= 3.10
- MySQL >= 8.0
- Redis >= 7.0

### 前端启动

```bash
cd pc

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview
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

# 数据库配置
DB_NAME=sxsinfo
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

# 密码加密密钥
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

## API 文档

启动后端服务后访问：
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## 用户角色

| 角色 | 权限 |
|------|------|
| 超级管理员 | 全部权限 |
| 系统管理员 | 用户管理、系统配置 |
| 实训室管理员 | 实训室管理、设备管理 |
| 教师 | 使用记录、维护申请 |
| 普通用户 | 查看权限 |

## 部署说明

### Docker 部署

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 生产环境

1. 使用 Gunicorn + Gevent 作为 WSGI 服务器
2. 使用 Nginx 反向代理静态资源
3. 配置 HTTPS 证书
4. 配置 Redis 缓存
5. 配置 Celery 异步任务

## 开发规范

### 前端

- 使用 Composition API 编写组件
- 使用 Pinia 管理全局状态
- 使用 hooks 封装可复用逻辑
- 遵循 Vue 3 风格指南
- 支持 TypeScript 渐进式迁移

### 后端

- 使用 Django REST Framework 构建 API
- 使用 Services 层封装业务逻辑
- 使用 Serializers 处理数据序列化
- 使用 Celery 处理异步任务
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

# 生成覆盖率报告
pytest --cov=apps
```

## 作者

LIMS Team
