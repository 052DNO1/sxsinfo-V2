#!/bin/bash

# ╔═══════════════════════════════════════════════════════╗
# ║     LIMS 智能实验室管理系统 - Linux 一键部署工具      ║
# ║     支持: Ubuntu 24.04+ / Debian 12+ / CentOS 9+       ║
# ╚═══════════════════════════════════════════════════════╝
#
# 使用方法:
#   chmod +x deploy.sh
#   ./deploy.sh
#
# 或直接运行:
#   bash deploy.sh

set -e

# ============================================
# 颜色定义
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# ============================================
# 全局变量
# ============================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"

# ============================================
# 工具函数
# ============================================

print_header() {
    echo -e "\n${CYAN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC} ${BOLD}🚀 LIMS 智能实验室管理系统 部署工具${NC}        ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}    ${GREEN}全自动 · 零配置 · 开箱即用${NC}              ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}\n"
}

print_step() {
    echo -e "${BLUE}[$1/6] $2${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME=$NAME
        OS_VERSION=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS_NAME=$(lsb_release -si)
        OS_VERSION=$(lsb_release -sr)
    else
        OS_NAME=$(uname -s)
        OS_VERSION=$(uname -r)
    fi
    
    print_info "检测到系统: $OS_NAME $OS_VERSION"
}

# ============================================
# 第一步：检查 Docker 环境
# ============================================
check_docker() {
    print_step "1" "🔍 检查运行环境..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        print_warning "未检测到 Docker，正在安装..."
        install_docker
    else
        print_success "Docker 已安装: $(docker --version)"
    fi
    
    # 检查 Docker Compose
    if ! docker compose version &> /dev/null; then
        if ! command -v docker-compose &> /dev/null; then
            print_warning "未检测到 Docker Compose，正在安装..."
            install_docker_compose
        else
            print_success "Docker Compose (standalone): $(docker-compose --version)"
        fi
    else
        print_success "Docker Compose (plugin): $(docker compose version)"
    fi
    
    # 检查 Docker 是否运行
    if ! docker info &> /dev/null; then
        print_error "Docker 服务未运行！"
        print_info "请启动 Docker 服务:"
        echo "  sudo systemctl start docker"
        echo "  sudo systemctl enable docker"
        exit 1
    fi
    
    print_success "环境检查通过 ✓"
}

install_docker() {
    print_info "正在安装 Docker..."
    
    # 检测包管理器
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # 添加 Docker 官方 GPG key
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        # 设置仓库
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # 安装 Docker
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        # 启动服务
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # 将当前用户添加到 docker 组
        sudo usermod -aG docker $USER
        print_warning "已将当前用户 '$USER' 添加到 docker 组"
        print_info "请执行 'newgrp docker' 或重新登录以生效"
        
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL/Fedora
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
        
    elif command -v dnf &> /dev/null; then
        # Fedora
        sudo dnf -y install dnf-plugins-core
        sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
        sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    else
        print_error "无法识别的包管理器，请手动安装 Docker"
        print_info "访问: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    print_success "Docker 安装完成"
}

install_docker_compose() {
    print_info "正在安装 Docker Compose..."
    
    # 获取最新版本
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)
    
    sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_success "Docker Compose 安装完成: $(docker-compose --version)"
}

# ============================================
# 第二步：创建目录
# ============================================
create_directories() {
    print_step "2" "📁 准备工作目录..."
    
    local dirs=(
        "nginx/logs"
        "ssl/certs"
        "backend-v2/sql"
        "backend-v2/media"
        "backend-v2/logs"
    )
    
    for dir in "${dirs[@]}"; do
        full_path="${SCRIPT_DIR}/${dir}"
        if [ ! -d "$full_path" ]; then
            mkdir -p "$full_path"
            print_info "创建目录: $dir"
        fi
    done
    
    # 设置权限
    chmod -R 755 "${SCRIPT_DIR}/nginx" 2>/dev/null || true
    chmod -R 755 "${SCRIPT_DIR}/backend-v2" 2>/dev/null || true
    
    print_success "目录已就绪"
}

# ============================================
# 第三步：智能环境配置
# ============================================
configure_env() {
    print_step "3" "⚙️ 配置部署参数..."
    
    local need_config=0
    
    # 检查 .env 文件
    if [ -f "$ENV_FILE" ]; then
        # 检查是否有默认值或空值
        if grep -qE "(change-me|^SECRET_KEY=$|^DB_PASSWORD=$)" "$ENV_FILE" 2>/dev/null; then
            need_config=1
            print_warning "检测到 .env 文件但配置不完整"
        else
            print_success "检测到完整配置 (.env)"
            
            read -p "是否使用现有配置？[Y/n]: " reuse_config
            reuse_config=${reuse_config:-Y}
            
            if [[ ! "$reuse_config" =~ ^[Yy]$ ]]; then
                need_config=1
            fi
        fi
    else
        need_config=1
        print_warning "未找到 .env 文件"
    fi
    
    if [ $need_config -eq 1 ]; then
        generate_env
    fi
    
    # 读取配置用于显示
    source "$ENV_FILE" 2>/dev/null || true
    SERVER_PORT=${SERVER_PORT:-80}
}

generate_env() {
    echo ""
    echo -e "${CYAN}┌─────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC}     ${BOLD}🎯 首次部署配置向导${NC}              ${CYAN}│${NC}"
    echo -e "${CYAN}│${NC}     (跟着提示输入即可，回车使用默认值)  ${CYAN}│${NC}"
    echo -e "${CYAN}└─────────────────────────────────────────┘${NC}"
    echo ""
    
    # 生成 Django SECRET_KEY
    print_info "生成 Django 安全密钥..."
    DJANGO_KEY=""
    
    if command -v python3 &> /dev/null; then
        DJANGO_KEY=$(python3 -c "
import secrets
print(secrets.token_urlsafe(50))
" 2>/dev/null || echo "")
    fi
    
    if [ -z "$DJANGO_KEY" ]; then
        DJANGO_KEY=$(openssl rand -hex 32 2>/dev/null || date +%s%N | sha256sum | head -c 50)
    fi
    
    print_success "密钥已生成: ${DJANGO_KEY:0:20}..."
    
    read -ep "Django密钥 [自动生成]: " input_secret
    SECRET_KEY="${input_secret:-$DJANGO_KEY}"
    
    echo ""
    
    # 数据库密码
    read -sp "数据库密码 [lims2024secure]: " input_db_pass
    DB_PASSWORD="${input_db_pass:-lims2024secure}"
    echo ""
    
    read -sp "MySQL Root密码 [root2024secure]: " input_root_pass
    DB_ROOT_PASSWORD="${input_root_pass:-root2024secure}"
    echo ""
    
    echo ""
    
    # 加密密钥（32位）
    print_info "生成密码加密密钥(32位)..."
    ENCRYPT_KEY=""
    
    if command -v openssl &> /dev/null; then
        ENCRYPT_KEY=$(openssl rand -base64 32 | tr -d '\n' | head -c 32)
    elif command -v python3 &> /dev/null; then
        ENCRYPT_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
    else
        ENCRYPT_KEY=$(date +%s%N | md5sum | head -c 32)
    fi
    
    print_success "加密密钥已生成: ${ENCRYPT_KEY:0:16}..."
    
    read -sp "密码加密密钥(32位) [自动生成]: " input_encrypt
    PASSWORD_ENCRYPT_KEY="${input_encrypt:-$ENCRYPT_KEY}"
    echo ""
    
    echo ""
    
    # 服务器端口
    read -ep "服务端口 [80]: " input_port
    SERVER_PORT="${input_port:-80}"
    
    # 允许的主机
    read -ep "允许的域名(逗号分隔) [*]: " input_hosts
    ALLOWED_HOSTS="${input_hosts:-*}"
    
    echo ""
    
    # DeepSeek AI（可选）
    read -ep "DeepSeek API Key [跳过]: " DEEPSEEK_API_KEY
    
    # 写入 .env 文件
    echo ""
    print_info "正在生成 .env 配置文件..."
    
    cat > "$ENV_FILE" << EOF
# LIMS 环境配置 - 由部署脚本自动生成
# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')

# ── Django 后端 ──
SECRET_KEY=${SECRET_KEY}
ALLOWED_HOSTS=${ALLOWED_HOSTS}
CORS_ALLOWED_ORIGINS=*
PASSWORD_ENCRYPT_KEY=${PASSWORD_ENCRYPT_KEY}

# ── 前端构建变量 (VITE_ 前缀) ──
VITE_PASSWORD_ENCRYPT_KEY=${PASSWORD_ENCRYPT_KEY}
VITE_API_V2_BASE_URL=/api/v1

# ── MySQL 数据库 ──
DB_NAME=lims
DB_USER=lims
DB_PASSWORD=${DB_PASSWORD}
DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD}

# ── 服务端口 ──
SERVER_PORT=${SERVER_PORT}
HTTPS_PORT=443

# ── AI 功能 (可选) ──
DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
DEEPSEEK_SERVICE_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat
EOF
    
    chmod 600 "$ENV_FILE"  # 安全：只有所有者可读写
    print_success "配置已保存到 .env (共13项配置，权限已设为600)"
}

# ============================================
# 第四步：显示配置摘要
# ============================================
show_summary() {
    print_step "4" "📋 当前配置摘要:"
    
    echo -e "\n┌──────────────────────────────────────────┐"
    echo -e "│  ${BOLD}服务端口:${NC}    http://localhost:${SERVER_PORT}           │"
    echo -e "│  ${BOLD}PC端访问:${NC}    http://localhost:${SERVER_PORT}/            │"
    echo -e "│  ${BOLD}移动端访问:${NC}  http://localhost:${SERVER_PORT}/m/          │"
    echo -e "│  ${BOLD}API地址:${NC}     http://localhost:${SERVER_PORT}/api/v1/     │"
    echo -e "└──────────────────────────────────────────┘\n"
}

# ============================================
# 第五步：选择操作
# ============================================
show_menu() {
    print_step "5" "🎮 请选择操作:\n"
    
    echo "  1️⃣  🚀 完整部署（构建+启动）- 首次推荐"
    echo "  2️⃣  🔨 仅重建前端（代码更新后）"
    echo "  3️⃣  🔄 重启服务"
    echo "  4️⃣  📊 查看日志"
    echo "  5️⃣  🛑 停止所有服务"
    echo "  6️⃣  🧹 清理重来（删除数据重新部署）"
    echo "  7️⃣  🔧 进入容器终端"
    echo "  8️⃣  🔍 查看服务状态"
    echo "  9️⃣  💾 数据库备份"
    echo "  0️⃣  ❌ 退出"
    echo ""
    
    read -ep "请输入选项 [0-9]: " choice
    
    case $choice in
        1) full_deploy ;;
        2) rebuild_frontend ;;
        3) restart_services ;;
        4) view_logs ;;
        5) stop_all ;;
        6) clean_rebuild ;;
        7) shell_access ;;
        8) check_status ;;
        9) backup_database ;;
        0) exit_script ;;
        *) 
            print_error "无效选项"
            show_menu
            ;;
    esac
}

# ============================================
# 功能实现
# ============================================

full_deploy() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    echo -e "${CYAN}${BOLD}  🚀 开始完整部署...${NC}"
    echo -e "${CYAN}════════════════════════════════════════════${NC}\n"
    
    print_info "[1/4] 停止旧容器..."
    cd "$SCRIPT_DIR"
    docker compose down --remove-orphans 2>/dev/null || true
    
    print_info "[2/4] 构建镜像（首次需要几分钟，请耐心等待）..."
    echo "    ├─ 构建 PC端前端..."
    docker compose build --no-cache frontend-pc || {
        print_error "PC端构建失败！"
        docker compose logs frontend-pc
        exit 1
    }
    print_success "PC端完成"
    
    echo "    ├─ 构建移动端前端..."
    docker compose build --no-cache frontend-mobile || {
        print_error "移动端构建失败！"
        docker compose logs frontend-mobile
        exit 1
    }
    print_success "移动端完成"
    
    echo "    ├─ 构建后端服务..."
    docker compose build --no-cache backend || {
        print_error "后端构建失败！"
        docker compose logs backend
        exit 1
    }
    print_success "后端完成"
    
    print_info "[3/4] 启动所有服务..."
    docker compose up -d || {
        print_error "启动失败！"
        docker compose logs
        exit 1
    }
    
    print_info "[4/4] 等待服务就绪..."
    wait_for_service 30
    
    show_status
}

rebuild_frontend() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    echo -e "${CYAN}${BOLD}  🔨 重新构建前端...${NC}"
    echo -e "${CYAN}════════════════════════════════════════════${NC}\n"
    
    cd "$SCRIPT_DIR"
    docker compose build --no-cache frontend-pc frontend-mobile
    docker compose up -d nginx
    wait_for_service 10
    show_status
}

restart_services() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    echo -e "${CYAN}${BOLD}  🔄 重启服务...${NC}"
    echo -e "${CYAN}════════════════════════════════════════════${NC}\n"
    
    cd "$SCRIPT_DIR"
    docker compose restart
    wait_for_service 10
    show_status
}

view_logs() {
    echo ""
    echo "请选择要查看的服务日志:"
    echo "  1. 全部服务"
    echo "  2. 后端 (Django)"
    echo "  3. Nginx (反向代理)"
    echo "  4. 数据库 (MySQL)"
    echo "  5. Redis (缓存)"
    echo "  6. PC端构建"
    echo "  7. 移动端构建"
    echo "  0. 返回"
    echo ""
    
    read -ep "选择 [0-7]: " log_choice
    
    cd "$SCRIPT_DIR"
    
    case $log_choice in
        1) docker compose logs -f --tail=100 ;;
        2) docker compose logs -f --tail=100 backend ;;
        3) docker compose logs -f --tail=100 nginx ;;
        4) docker compose logs -f --tail=100 db ;;
        5) docker compose logs -f --tail=100 redis ;;
        6) docker compose logs -f --tail=100 frontend-pc ;;
        7) docker compose logs -f --tail=100 frontend-mobile ;;
        0|*) return ;;
    esac
}

stop_all() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    echo -e "${CYAN}${BOLD}  🛑 停止所有服务...${NC}"
    echo -e "${CYAN}════════════════════════════════════════════${NC}\n"
    
    cd "$SCRIPT_DIR"
    docker compose down
    
    echo ""
    print_success "所有服务已停止"
    print_info "数据已保留，下次启动不会丢失"
}

clean_rebuild() {
    echo ""
    echo -e "${RED}════════════════════════════════════════════${NC}"
    echo -e "${RED}${BOLD}  ⚠️  警告：此操作将删除所有数据！${NC}"
    echo -e "${RED}════════════════════════════════════════════${NC}\n"
    
    read -ep "确定要清理并完全重新部署吗？(y/N): " confirm
    
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        print_info "删除容器、镜像和数据卷..."
        cd "$SCRIPT_DIR"
        docker compose down -v --remove-orphans
        docker system prune -af --volumes
        
        print_info "重新构建并启动..."
        docker compose build --no-cache
        docker compose up -d
        wait_for_service 30
        show_status
    else
        print_info "已取消"
    fi
}

shell_access() {
    echo ""
    echo "请选择要进入的容器:"
    echo "  1. 后端 (Django)"
    echo "  2. 数据库 (MySQL)"
    echo "  3. Redis"
    echo "  4. Nginx"
    echo "  0. 返回"
    echo ""
    
    read -ep "选择 [0-4]: " shell_choice
    
    cd "$SCRIPT_DIR"
    
    case $shell_choice in
        1) docker exec -it lims_backend bash ;;
        2) source "$ENV_FILE" && docker exec -it lims_db mysql -u root -p"$DB_ROOT_PASSWORD" lims ;;
        3) docker exec -it lims_redis redis-cli ;;
        4) docker exec -it lims_nginx sh ;;
        0|*) return ;;
    esac
}

check_status() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    echo -e "${CYAN}${BOLD}  📊 服务运行状态${NC}"
    echo -e "${CYAN}════════════════════════════════════════════${NC}\n"
    
    cd "$SCRIPT_DIR"
    docker compose ps
    
    echo ""
    print_info "资源占用:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

backup_database() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    echo -e "${CYAN}${BOLD}  💾 数据库备份${NC}"
    echo -e "${CYAN}════════════════════════════════════════════${NC}\n"
    
    cd "$SCRIPT_DIR"
    source "$ENV_FILE" 2>/dev/null || true
    
    BACKUP_DIR="${SCRIPT_DIR}/backups"
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    BACKUP_FILE="${BACKUP_DIR}/lims_backup_${TIMESTAMP}.sql"
    
    print_info "正在备份数据库到: $BACKUP_FILE"
    
    docker exec lims_db mysqldump -u root -p"${DB_ROOT_PASSWORD}" lims > "$BACKUP_FILE" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        gzip "$BACKUP_FILE"
        print_success "备份完成: ${BACKUP_FILE}.gz"
        
        # 显示文件大小
        FILE_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
        print_info "文件大小: $FILE_SIZE"
        
        # 清理旧备份（保留最近7个）
        ls -t "${BACKUP_DIR}"/*.sql.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true
        print_info "已清理旧备份（保留最近7个）"
    else
        print_error "备份失败！"
    fi
}

wait_for_service() {
    local max_wait=$1
    local waited=0
    
    print_info "等待服务启动（最多 ${max_wait} 秒）..."
    
    while [ $waited -lt $max_wait ]; do
        sleep 2
        waited=$((waited + 2))
        printf "\r    已等待 %ds/%ds ..." $waited $max_wait
    done
    
    echo ""
}

show_final_info() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    echo -e "${GREEN}${BOLD}  ✅ 部署完成！${NC}"
    echo -e "${CYAN}════════════════════════════════════════════${NC}\n"
    
    echo -e "${BOLD}🌐 访问地址:${NC}"
    echo "    ┌────────────────────────────────────┐"
    echo "    │  ${BOLD}🖥️ PC端:${NC}  http://localhost:${SERVER_PORT}/      │"
    echo "    │  ${BOLD}📱 移动端:${NC} http://localhost:${SERVER_PORT}/m/    │"
    echo "    │  ${BOLD}🔌 API:${NC}   http://localhost:${SERVER_PORT}/api/v1/│"
    echo "    │  ${BOLD}❤️ 健康:${NC}  http://localhost:${SERVER_PORT}/health │"
    echo "    └────────────────────────────────────┘"
    echo ""
    
    echo -e "${BOLD}📝 默认账号（如果有初始化数据）:${NC}"
    echo "    用户名: admin"
    echo "    密码: admin123"
    echo ""
    
    # 获取局域网IP
    LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || ip route get 1 | awk '{print $7; exit}')
    
    if [ -n "$LAN_IP" ] && [ "$LAN_IP" != "127.0.0.1" ]; then
        echo -e "${BOLD}📱 局域网访问（手机同WiFi下）:${NC}"
        echo "    PC端:  http://${LAN_IP}:${SERVER_PORT}/"
        echo "    移动端: http://${LAN_IP}:${SERVER_PORT}/m/"
        echo ""
    fi
    
    echo -e "${BOLD}🔧 常用命令:${NC}"
    echo "    查看日志: ./deploy.sh → 选择 4"
    echo "    重启服务: ./deploy.sh → 选择 3"
    echo "    停止服务: ./deploy.sh → 选择 5"
    echo "    数据库备份: ./deploy.sh → 选择 9"
    echo ""
    echo -e "${BOLD}📖 详细文档:${NC} DEPLOY.md\n"
}

exit_script() {
    echo ""
    print_info "再见！👋"
    exit 0
}

# ============================================
# 主程序入口
# ============================================
main() {
    print_header
    
    detect_os
    check_docker
    create_directories
    configure_env
    show_summary
    show_menu
    show_final_info
    
    echo ""
    read -ep "按回车键退出..." 
}

# 运行主程序
main "$@"