import secrets
import os
import socket
import subprocess
from datetime import datetime

def get_local_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except Exception:
        return "localhost"

def check_docker():
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except Exception:
        return False

def get_docker_compose_command():
    try:
        subprocess.run(["docker", "compose", "version"], check=True, capture_output=True)
        return "docker compose"
    except Exception:
        try:
            subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
            return "docker-compose"
        except Exception:
            return None

def run_docker_compose():
    docker_cmd = get_docker_compose_command()
    if not docker_cmd:
        print("❌ 未找到 docker compose 命令")
        print("请先安装 Docker Compose")
        return False
    
    print(f"正在构建并启动服务（无缓存构建）...")
    try:
        cmd = docker_cmd.split()
        cmd.extend(["build", "--no-cache"])
        subprocess.run(cmd, check=True)
        
        cmd = docker_cmd.split()
        cmd.extend(["up", "-d"])
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动服务失败: {e}")
        return False

def generate_env_file():
    print("╔════════════════════════════════════════════════════╗")
    print("║       实训室信息管理系统 - 一键部署脚本          ║")
    print("╚════════════════════════════════════════════════════╝")
    print()

    if not check_docker():
        print("❌ Docker 未安装，请先安装 Docker")
        return

    detected_ip = get_local_ip()
    print(f"自动检测到本机IP: {detected_ip}")
    SERVER_IP = input(f"请输入服务器访问IP地址 [默认: {detected_ip}]: ").strip() or detected_ip
    SERVER_PORT = input("请输入服务访问端口 [默认: 8080]: ").strip() or "8080"
    print()

    DB_NAME = input("请输入数据库名称 [默认: sxsinfo]: ").strip() or "sxsinfo"
    DB_PASSWORD = input("请输入数据库密码 [默认: YourStrongPassword123]: ").strip() or "YourStrongPassword123"
    DB_ROOT_PASSWORD = input("请输入Root密码 [默认: 128076]: ").strip() or "128076"
    
    print()
    print("【DeepSeek API 配置】")
    print("  如需使用 DeepSeek AI 功能，请输入 API Key")
    print("  获取地址: https://platform.deepseek.com/")
    DEEPSEEK_API_KEY = input("请输入DeepSeek API Key [留空跳过]: ").strip()
    DEEPSEEK_SERVICE_URL = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_MODEL = "deepseek-chat"
    
    SECRET_KEY = secrets.token_urlsafe(50)
    ENCRYPT_KEY = secrets.token_urlsafe(32)[:32]
    
    env_content = f"""# ============================================
# 生产环境配置 (自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
# ============================================

# Django 密钥
SECRET_KEY={SECRET_KEY}

# 允许的主机 (Django会按逗号分割)
ALLOWED_HOSTS={SERVER_IP},localhost,127.0.0.1

# 服务端口
SERVER_PORT={SERVER_PORT}

# CORS 允许的前端域名 (会被追加到默认列表)
# 注意：settings.py中已有默认配置，这里只需要添加生产环境的地址
CORS_ALLOWED_ORIGINS=http://{SERVER_IP}:{SERVER_PORT},http://{SERVER_IP}

# 数据库配置
DB_NAME={DB_NAME}
DB_PASSWORD={DB_PASSWORD}
DB_ROOT_PASSWORD={DB_ROOT_PASSWORD}

# 密码加密密钥 (前后端必须相同)
PASSWORD_ENCRYPT_KEY={ENCRYPT_KEY}
VITE_PASSWORD_ENCRYPT_KEY={ENCRYPT_KEY}

# DeepSeek API 配置
DEEPSEEK_API_KEY={DEEPSEEK_API_KEY}
DEEPSEEK_SERVICE_URL={DEEPSEEK_SERVICE_URL}
DEEPSEEK_MODEL={DEEPSEEK_MODEL}
"""

    env_file = ".env"
    
    if os.path.exists(env_file):
        overwrite = input(f"{env_file} 已存在，是否覆盖？[Y/n]: ").strip().lower()
        if overwrite not in ['', 'y', 'yes']:
            print("已取消生成")
            return
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print()
    print("✅ .env 文件已生成成功！")
    print()
    print("生成的加密配置：")
    print("=" * 50)
    print(f"SECRET_KEY={SECRET_KEY}")
    print(f"PASSWORD_ENCRYPT_KEY={ENCRYPT_KEY}")
    print(f"VITE_PASSWORD_ENCRYPT_KEY={ENCRYPT_KEY}")
    print("=" * 50)
    print()
    print("配置摘要：")
    print(f"  服务器IP: {SERVER_IP}")
    print(f"  服务端口: {SERVER_PORT}")
    print(f"  数据库名称: {DB_NAME}")
    print(f"  数据库密码: {DB_PASSWORD}")
    print(f"  Root密码: {DB_ROOT_PASSWORD}")
    if DEEPSEEK_API_KEY:
        print(f"  DeepSeek API Key: {DEEPSEEK_API_KEY[:8]}...{DEEPSEEK_API_KEY[-4:]}")
    else:
        print(f"  DeepSeek API Key: 未配置")
    print(f"  ALLOWED_HOSTS: {SERVER_IP},localhost,127.0.0.1")
    print(f"  CORS_ALLOWED_ORIGINS: http://{SERVER_IP}:{SERVER_PORT},http://{SERVER_IP}")
    print()
    print("重要说明：")
    print("  1. DJANGO_ENV=production 已在 docker-compose.yml 中设置")
    print("  2. ALLOWED_HOSTS 会被 Django 按逗号分割")
    print("  3. CORS_ALLOWED_ORIGINS 会被追加到默认列表")
    print("  4. 默认CORS配置已包含 localhost:5173, localhost:8080 等")
    print()

    start_services = input("是否立即启动Docker服务？[Y/n]: ").strip().lower()
    if start_services not in ['', 'y', 'yes']:
        print("已跳过服务启动")
        return

    print()
    print("【步骤 1/2】启动Docker服务")
    if not run_docker_compose():
        print("❌ 服务启动失败")
        return

    print()
    print("【步骤 2/2】等待服务启动...")
    print("等待30秒让服务完全启动...")
    import time
    time.sleep(30)

    print()
    print("╔════════════════════════════════════════════════════╗")
    print("║              部署完成！                           ║")
    print("╚════════════════════════════════════════════════════╝")
    print()
    print(f"🌐 访问地址: http://{SERVER_IP}:{SERVER_PORT}")
    print()
    print("📋 常用命令：")
    docker_cmd = get_docker_compose_command()
    print(f"  查看状态: {docker_cmd} ps")
    print(f"  查看日志: {docker_cmd} logs -f")
    print(f"  重启服务: {docker_cmd} restart")
    print(f"  停止服务: {docker_cmd} down")
    print()
    print("🤖 AI功能说明：")
    if DEEPSEEK_API_KEY:
        print(f"  - DeepSeek API: 已配置")
    else:
        print(f"  - DeepSeek API: 未配置 (可在 .env 中手动添加)")
    print()

if __name__ == "__main__":
    generate_env_file()
