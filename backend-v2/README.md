# LIMS Backend

实训室信息管理系统后端

## 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.0+
- Redis 7.0+

### 安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements/development.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 数据库迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

## 项目结构

```
lims_backend/
├── apps/                   # 应用模块
│   ├── core/              # 核心基础模块
│   ├── users/             # 用户管理
│   ├── laboratories/      # 实训室管理
│   ├── schedules/         # 课表管理
│   ├── records/           # 使用记录
│   ├── maintenance/       # 维护管理
│   ├── notifications/     # 通知模块
│   ├── ai_assistant/      # AI助手
│   ├── backup/            # 备份恢复
│   └── statistics/        # 统计分析
├── common/                # 公共模块
├── utils/                 # 工具函数
├── extensions/            # 扩展模块
├── api/                   # API路由
├── lims/                  # 项目配置
└── manage.py
```

## API文档

启动服务后访问: http://localhost:8000/api/docs/
