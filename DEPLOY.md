# LIMS Docker 部署文档

## 📋 目录结构

```
d:\project\V2\
├── docker-compose.yml          # Docker 编排文件
├── deploy.bat                  # Windows 一键部署脚本
├── .env.example                # 环境变量模板
├── .env                        # 环境变量配置（需手动创建）
│
├── frontend/                   # 前端源码
│   ├── Dockerfile.pc           # PC端构建配置
│   ├── Dockerfile.mobile       # 移动端构建配置
│   └── ...
│
├── backend-v2/                 # 后端 Django 源码
│   ├── Dockerfile              # 后端构建配置
│   └── ...
│
└── nginx/                      # Nginx 配置
    ├── nginx.conf              # 主配置文件
    └── conf.d/
        └── default.conf        # 站点配置
```

## 🚀 快速开始

### 1️⃣ 安装依赖

**Windows:**
```powershell
# 安装 Docker Desktop for Windows
# 下载地址: https://www.docker.com/products/docker-desktop/
```

**Linux:**
```bash
# 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
sudo systemctl start docker
sudo systemctl enable docker
```

### 2️⃣ 配置环境变量

```bash
# 复制环境变量模板
copy .env.example .env

# 编辑配置文件（必填项）
notepad .env  # Windows
nano .env     # Linux/Mac
```

**必须修改的配置：**

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `SECRET_KEY` | Django 密钥 | `django-insecure-xxx...` |
| `DB_PASSWORD` | 数据库密码 | `MySecurePassword123` |
| `DB_ROOT_PASSWORD` | MySQL Root密码 | `RootPassword456` |
| `PASSWORD_ENCRYPT_KEY` | 密码加密密钥(32位) | `abcdefghijklmnopqrstuvwxyz1234` |

**生成密钥命令：**

```bash
# 生成 SECRET_KEY (Django)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 生成 PASSWORD_ENCRYPT_KEY (32位)
openssl rand -base64 32 | head -c 32
```

### 3️⃣ 一键部署

**Windows:**
```powershell
# 双击运行或命令行执行
deploy.bat
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### 4️⃣ 访问系统

| 服务 | 地址 | 说明 |
|------|------|------|
| **PC端** | http://localhost/ | 电脑浏览器访问 |
| **移动端** | http://localhost/m/ | 手机/平板访问 |
| **API** | http://localhost/api/v1/ | 后端接口 |
| **健康检查** | http://localhost/health | 服务状态检测 |

---

## 🔧 手动操作

### 构建服务

```bash
# 构建所有服务
docker-compose build

# 仅构建前端
docker-compose build frontend-pc frontend-mobile

# 仅构建后端
docker-compose build backend
```

### 启动/停止

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 启动并查看日志
docker-compose up

# 停止所有服务
docker-compose down

# 重启某个服务
docker-compose restart nginx
```

### 查看日志

```bash
# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f nginx

# 查看最近100行日志
docker-compose logs --tail=100
```

### 进入容器

```bash
# 进入后端容器
docker exec -it lims_backend bash

# 进入数据库容器
docker exec -it lims_db mysql -u root -p

# 进入 Redis 容器
docker exec -it lims_redis redis-cli
```

---

## 📱 移动端访问方式

### 方式1：自动跳转（推荐）

Nginx 会根据 User-Agent 自动识别设备类型：
- **电脑** → 自动显示 PC 端
- **手机/平板** → 自动跳转到 `/m/` 显示移动端

### 方式2：直接访问

- PC端：http://your-server-ip/
- 移动端：http://your-server-ip/m/

---

## 🔒 HTTPS 配置（可选）

### 使用 Let's Encrypt 免费证书

```bash
# 1. 安装 Certbot
apt install certbot python3-certbot-nginx  # Ubuntu/Debian

# 2. 获取证书（替换 your-domain.com）
certbot --nginx -d your-domain.com

# 3. 自动续期已配置，测试续期
certbot renew --dry-run
```

### 或使用自签名证书（开发环境）

```bash
# 生成证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/certs/key.pem \
  -out ssl/certs/cert.pem \
  -subj "/CN=localhost"

# 更新 Nginx 配置添加 HTTPS 支持
# （见 nginx/conf.d/default.conf）
```

---

## 🐛 常见问题排查

### 问题1：端口被占用

```bash
# 查看占用端口的进程
netstat -ano | findstr :80  # Windows
lsof -i :80                 # Linux/Mac

# 解决方案：修改 .env 中的 SERVER_PORT
SERVER_PORT=8080
```

### 问题2：数据库连接失败

```bash
# 查看数据库日志
docker-compose logs db

# 常见原因：
# 1. 密码错误 → 检查 .env 中的 DB_PASSWORD
# 2. 数据库未初始化 → 等待更长时间让 MySQL 完成
# 3. 字符集问题 → 确保 MySQL 配置了 utf8mb4
```

### 问题3：前端构建失败

```bash
# 清理缓存重新构建
docker-compose build --no-cache frontend-pc frontend-mobile

# 查看构建日志
docker-compose build frontend-pc 2>&1 | tee build.log
```

### 问题4：静态文件 404

```bash
# 收集 Django 静态文件
docker exec -it lims_backend python manage.py collectstatic --noinput

# 重启 Nginx
docker-compose restart nginx
```

### 问题5：查看容器资源占用

```bash
# 查看所有容器状态
docker stats

# 查看特定容器详情
docker inspect lims_backend
```

---

## 📊 性能优化建议

### 1. 调整 Worker 数量

根据服务器 CPU 核心数调整：

```bash
# 在 backend-v2/Dockerfile 中修改
CMD ["gunicorn", "lims.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]

# 推荐公式：CPU核心数 * 2 + 1
```

### 2. Redis 持久化

```yaml
# 在 docker-compose.yml 的 redis 服务中添加
command: redis-server --appendonly yes
volumes:
  - redis_data:/data
```

### 3. 数据库备份

```bash
# 手动备份数据库
docker exec lims_db mysqldump -u root -p${DB_ROOT_PASSWORD} lims > backup_$(date +%Y%m%d).sql

# 定时备份（添加到 crontab）
0 2 * * * docker exec lims_db mysqldump ... > /backup/daily.sql
```

### 4. 日志轮转

在 `docker-compose.yml` 中添加：

```yaml
services:
  backend:
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "3"
```

---

## 🔐 安全建议

1. **修改默认密码** - 务必修改 `.env` 中的所有密码
2. **限制网络访问** - 只开放必要端口（80, 443）
3. **定期更新** - 定期更新 Docker 镜像和依赖包
4. **启用 HTTPS** - 生产环境务必使用 SSL/TLS
5. **防火墙规则** - 配置防火墙只允许必要的入站连接

---

## 📞 技术支持

如遇问题，请按以下顺序排查：

1. ✅ 检查 `.env` 配置是否正确
2. ✅ 运行 `docker-compose ps` 查看服务状态
3. ✅ 查看 `docker-compose logs` 错误日志
4. ✅ 确认端口未被占用
5. ✅ 检查防火墙设置

祝部署顺利！🎉