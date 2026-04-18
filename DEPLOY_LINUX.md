# LIMS Docker 部署指南 - Ubuntu 25.04 专用

## 🎯 快速开始（3步搞定）

### 第1步：安装依赖
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y curl wget git vim

# 安装 Docker（脚本会自动检测并提示安装，也可手动安装）
curl -fsSL https://get.docker.com | sh

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker  # 或注销重新登录

# 验证安装
docker --version
docker compose version
```

### 第2步：克隆/进入项目目录
```bash
cd /opt  # 或你的项目目录
# git clone <your-repo-url>
cd V2  # 项目根目录
```

### 第3步：一键部署
```bash
# 赋予执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

**选择 1️⃣ 完整部署 → 一路回车或输入自定义密码 → 等待完成！**

---

## 📋 脚本功能清单

| 功能 | 说明 | 适用场景 |
|------|------|---------|
| **1️⃣ 完整部署** | 构建全部镜像 + 启动服务 | 首次使用 |
| **2️⃣ 重建前端** | 仅重新构建 PC端 + 移动端 | 前端代码更新后 |
| **3️⃣ 重启服务** | 重启所有容器 | 配置修改后 |
| **4️⃣ 查看日志** | 查看各服务实时日志 | 排查问题 |
| **5️⃣ 停止服务** | 停止所有容器 | 临时关闭 |
| **6️⃣ 清理重来** | 删除数据 + 重新部署 | 彻底重置 |
| **7️⃣ 进入容器** | Shell 访问容器内部 | 调试 |
| **8️⃣ 服务状态** | 查看运行状态 + 资源占用 | 监控 |
| **9️⃣ 数据库备份** | 自动备份 MySQL 到 backups/ | 定期备份 |

---

## 🔧 Ubuntu 25.04 特殊优化

### ✅ 已处理的兼容性问题

1. **Docker Compose V2 插件**
   - 自动检测 `docker compose` (V2) 和 `docker-compose` (V1)
   - 优先使用新版插件语法

2. **权限管理**
   - 自动将用户添加到 `docker` 组
   - `.env` 文件自动设置 `600` 权限（安全）
   - 目录权限自动设置为 `755`

3. **包管理器适配**
   - 支持 `apt` (Ubuntu/Debian)
   - 支持 `yum/dnf` (CentOS/Fedora/RHEL)

4. **网络检测**
   - 使用 `hostname -I` 或 `ip route` 获取局域网IP
   - 方便手机同WiFi访问

5. **字符编码**
   - 脚本头部设置 UTF-8 编码
   - 支持中文显示和输入密码

---

## 📁 文件结构说明

```
V2/
├── deploy.sh              # ⭐ Linux 部署脚本（你在这里）
├── deploy.bat             # Windows 部署脚本
├── docker-compose.yml     # Docker 编排（7个服务）
├── .env.example           # 环境变量模板
├── .env                   # 环境变量（自动生成）
│
├── frontend/              # 前端源码
│   ├── Dockerfile.pc      # PC端构建配置
│   ├── Dockerfile.mobile  # 移动端构建配置
│   └── ...
│
├── backend-v2/            # 后端 Django
│   ├── Dockerfile         # 后端构建配置
│   └── ...
│
├── nginx/                 # Nginx 配置
│   ├── nginx.conf         # 主配置
│   └── conf.d/
│       └── default.conf   # 站点配置 + 反向代理
│
├── ssl/certs/             # SSL证书目录（可选）
└── backups/               # 数据库备份目录（自动创建）
```

---

## 🌐 部署完成后访问

### 本地访问
```
PC端:    http://localhost:80/
移动端:  http://localhost:80/m/
API:     http://localhost:80/api/v1/
健康检查: http://localhost:80/health
```

### 局域网访问（手机同WiFi）
```bash
# 查看服务器IP
ip addr show | grep "inet " | grep -v 127.0.0.1

# 手机浏览器访问
http://<服务器IP>:80/        # PC端
http://<服务器IP>:80/m/      # 移动端
```

### 公网访问（需配置域名 + DNS）
```bash
# 1. 修改 .env
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# 2. 配置 DNS 解析到服务器IP

# 3. 可选：配置 HTTPS（Let's Encrypt）
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🔄 日常运维命令

### 快捷方式（通过脚本）
```bash
./deploy.sh          # 打开菜单
./deploy.sh          # 选 2 → 更新前端代码
./deploy.sh          # 选 9 → 备份数据库
```

### 手动命令（直接使用 Docker）
```bash
# 查看状态
docker compose ps
docker compose top

# 日志
docker compose logs -f                    # 全部
docker compose logs -f backend            # 后端
docker compose logs -f nginx              # Nginx

# 重启
docker compose restart                   # 重启全部
docker compose restart backend           # 重启后端

# 进入容器
docker exec -it lims_backend bash        # Django
docker exec -it lims_db mysql -u root -p # MySQL
docker exec -it lims_redis redis-cli     # Redis

# 清理
docker system prune -af                  # 清理无用镜像
```

---

## 💾 数据库备份与恢复

### 自动备份（推荐）
```bash
# 通过脚本
./deploy.sh → 选择 9️⃣

# 手动备份
mkdir -p backups
docker exec lims_db mysqldump -u root -p'YOUR_PASSWORD' lims | gzip > backups/backup_$(date +%Y%m%d).sql.gz
```

### 定时备份（Crontab）
```bash
# 编辑定时任务
crontab -e

# 添加以下行（每天凌晨2点备份）
0 2 * * * cd /path/to/V2 && ./deploy.sh << EOF
9
EOF
```

### 恢复备份
```bash
# 解压备份
gunzip backup_20240101.sql.gz

# 导入数据库
docker exec -i lims_db mysql -u root -p'YOUR_PASSWORD' lims < backup_20240101.sql
```

---

## ❓ 常见问题排查

### 问题1：Docker 权限错误
```bash
# 错误信息：Got permission denied while trying to connect to the Docker daemon socket

# 解决方案：
sudo usermod -aG docker $USER
newgrp docker    # 立即生效（仅当前终端）
# 或 注销重新登录
```

### 问题2：端口被占用
```bash
# 查看占用进程
sudo lsof -i :80
sudo netstat -tlnp | grep :80

# 解决方案：修改端口
vim .env
# SERVER_PORT=8080

# 重启服务
./deploy.sh → 选择 3️⃣
```

### 问题3：内存不足
```bash
# 查看内存使用
free -h
docker stats

# 解决方案：限制容器内存（编辑 docker-compose.yml）
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

### 问题4：前端构建失败
```bash
# 查看详细错误
docker compose logs frontend-pc

# 常见原因：
# 1. Node.js 版本不兼容 → 已固定为 node:22-alpine
# 2. 内存不足 → 增加 swap
# 3. 网络问题 → 检查代理设置

# 清理缓存重试
docker compose build --no-cache frontend-pc
```

### 问题5：数据库连接失败
```bash
# 查看 MySQL 日志
docker compose logs db

# 检查 .env 配置
grep DB_ .env

# 手动测试连接
docker exec -it lims_db mysql -u lims -p'YOUR_PASSWORD' -e "SELECT 1"
```

### 问题6：Nginx 502 Bad Gateway
```bash
# 检查后端是否运行
docker compose ps

# 检查后端健康状态
curl http://localhost:8000/api/v1/health/

# 查看 Nginx 错误日志
docker compose logs nginx | grep error
```

---

## 🔒 安全加固建议

### 1. 防火墙配置
```bash
# UFW（Ubuntu 默认防火墙）
sudo ufw enable
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw status

# 或使用 iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### 2. SSH 加固
```bash
sudo vim /etc/ssh/sshd_config

# 修改以下配置：
PermitRootLogin no
PasswordAuthentication yes  # 或 no（如果用密钥登录）
Port 2222                  # 改成非标准端口

sudo systemctl restart sshd
```

### 3. Fail2Ban（防暴力破解）
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 4. 自动更新
```bash
# 安装 unattended-upgrades
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## 📊 性能优化建议

### 1. 调整 Worker 数量
```bash
# 查看CPU核心数
nproc

# 编辑 backend-v2/Dockerfile
# CMD ["gunicorn", "lims.wsgi:application", "--workers", "4"]
# 推荐：CPU核心数 * 2 + 1
```

### 2. Redis 持久化
```yaml
# 在 docker-compose.yml 的 redis 服务中添加
command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### 3. 日志轮转
```yaml
# 在 docker-compose.yml 中添加
services:
  backend:
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "3"
```

### 4. Swap 分区（低内存机器）
```bash
# 创建 2GB swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 开机自动挂载
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 🆘 技术支持

### 收集诊断信息
```bash
# 创建诊断报告
{
    echo "=== 系统信息 ==="
    uname -a
    cat /etc/os-release
    
    echo -e "\n=== Docker 信息 ==="
    docker --version
    docker compose version
    docker info
    
    echo -e "\n=== 容器状态 ==="
    docker compose ps
    
    echo -e "\n=== 最近日志 ==="
    docker compose logs --tail=50
    
    echo -e "\n=== 磁盘空间 ==="
    df -h
    
    echo -e "\n=== 内存使用 ==="
    free -h
} > diagnostics.txt
```

---

## 📝 更新日志

### v2.0.0 (2024)
- ✅ 全面支持 Ubuntu 25.04 LTS
- ✅ 新增 Linux deploy.sh 脚本
- ✅ 自动环境检测和配置生成
- ✅ 数据库备份功能
- ✅ 容器资源监控
- ✅ 完整的故障排查文档

---

**祝部署顺利！如有问题请查看上方故障排查章节。** 🚀