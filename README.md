# 实训室信息管理系统 (SXSInfo)

一个基于 Vue 3 + Django 的实训室信息管理系统，支持 PC 端和移动端双端访问。

## 功能特性

- **实训室管理**：实训室信息增删改查、工位管理、管理员分配
- **课表管理**：课程排课、周次节次管理、教师关联
- **使用记录**：实训室使用情况记录、教师签名、设备状态
- **维护管理**：维护申请、维护记录、维护类型分类
- **设备管理**：设备信息录入、状态跟踪、位置管理
- **用户管理**：多角色用户、部门管理、权限分配
- **学期管理**：学期设置、数据归档
- **数据导入导出**：Excel 批量导入导出
- **统计报表**：使用统计、综合数据展示
- **双端适配**：自动识别设备，PC 端使用 Element Plus，移动端使用 Vant

## 技术栈

### 前端

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.5.x | 渐进式 JavaScript 框架 |
| Vite | 7.x | 下一代前端构建工具 |
| Vue Router | 4.x | 官方路由管理器 |
| Pinia | 3.x | Vue 状态管理库 |
| Element Plus | 2.x | PC 端 UI 组件库 |
| Vant | 4.x | 移动端 UI 组件库 |
| ECharts | 5.x | 数据可视化图表库 |
| Axios | 1.x | HTTP 请求库 |
| xlsx | 0.18.x | Excel 文件处理 |

### 后端

| 技术 | 版本 | 说明 |
|------|------|------|
| Django | 4.2.x | Python Web 框架 |
| Django REST Framework | 3.14.x | RESTful API 框架 |
| MySQL | - | 关系型数据库 |
| Redis | 5.x | 缓存服务 |
| Gunicorn | 21.x | WSGI 服务器 |

## 项目结构

```
052D_vue/
├── vue-project/                 # 前端项目
│   ├── src/
│   │   ├── assets/             # 静态资源
│   │   ├── components/         # 公共组件
│   │   ├── composables/        # 组合式函数 (Hooks)
│   │   ├── config/             # 配置文件
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── utils/              # 工具函数
│   │   └── views/              # 页面组件
│   │       ├── pc/             # PC 端页面
│   │       └── mobile/         # 移动端页面
│   ├── public/                 # 公共资源
│   └── package.json
│
└── backend/                    # 后端项目
    ├── sxs/                    # 实训室核心应用
    │   ├── models.py           # 数据模型
    │   ├── views/              # 视图函数
    │   ├── services/           # 业务逻辑层
    │   └── urls.py             # 路由配置
    ├── userinfo/               # 用户管理应用
    │   ├── models.py           # 用户、部门、学期模型
    │   ├── views/              # 视图函数
    │   └── services/           # 业务逻辑层
    ├── sxsinfo/                # 项目配置
    │   ├── settings.py         # Django 配置
    │   └── urls.py             # 主路由
    └── requirements.txt
```

## 快速开始

### 环境要求

- Node.js >= 20.19.0
- Python >= 3.10
- MySQL >= 5.7
- Redis >= 6.0

### 前端启动

```bash
cd vue-project

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
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

### 环境变量配置

后端需要在 `sxsinfo/settings.py` 或环境变量中配置：

```python
# 数据库配置
DATABASE_URL = 'mysql://user:password@localhost:3306/sxsinfo'

# Redis 配置
REDIS_URL = 'redis://localhost:6379/0'

# 密钥
SECRET_KEY = 'your-secret-key'
```

## 核心数据模型

### 实训室 (SXS)
- 实训室名称、门牌号、工位数
- 管理员、所属部门
- 状态、备注

### 课表 (SXSClass)
- 课程名称、星期、节次、周次
- 上课班级、任课教师
- 关联实训室、学期

### 使用记录 (SXSRecord)
- 使用日期、节次、学时
- 使用人数、实训内容
- 设备状态、教师签名

### 维护记录 (SXSMaintainRecord)
- 维护类型（检查维护/安全检查/设备维修）
- 维护内容、维护人员
- 请求时间、完成时间

### 设备 (Equipment)
- 设备编号、名称、品牌、型号
- CPU、内存、硬盘配置
- 位置、状态

## 路由懒加载

项目采用路由懒加载策略，每个页面独立打包：

```javascript
// 懒加载示例
{
  path: '/term',
  name: 'Term',
  component: () => import('@/views/pc/crud/list/TermList.vue')
}
```

优势：
- 首屏加载速度快
- 按需加载页面代码
- 清除缓存后不会长时间白屏

## 数据适配器

前端使用适配器模式处理后端数据：

```javascript
// utils/adapters.js
export const adaptClassList = (response) => {
  // 将后端数据转换为前端统一格式
  return { columns, data, pagination }
}
```

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
# 构建镜像
docker build -t sxsinfo .

# 运行容器
docker run -d -p 8000:8000 sxsinfo
```

### 生产环境

1. 使用 Gunicorn 作为 WSGI 服务器
2. 使用 Nginx 反向代理静态资源
3. 配置 HTTPS 证书
4. 配置 Redis 缓存

## 开发规范

### 前端

- 使用 Composition API 编写组件
- 使用 Pinia 管理全局状态
- 使用 composables 封装可复用逻辑
- 遵循 Vue 3 风格指南

### 后端

- 使用 Django REST Framework 构建 API
- 使用 Services 层封装业务逻辑
- 使用 Serializers 处理数据序列化
- 遵循 Django 最佳实践


## 作者

SXSInfo Team
