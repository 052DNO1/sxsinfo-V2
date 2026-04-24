@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

title LIMS 一键部署工具 (Windows)

echo.
echo ╔════════════════════════════════════════════╗
echo ║       🚀 LIMS 智能实验室管理系统 部署工具    ║
echo ║          全自动 · 零配置 · 开箱即用         ║
echo ╚════════════════════════════════════════════╝
echo.

:: ============================================
:: 第一步：检查并安装 Docker（全自动）
:: ============================================
echo [1/7] 🔍 检查运行环境...

call :check_docker
if %DOCKER_OK%==0 (
    echo.
    pause
    exit /b 1
)

:: 检查 Docker 是否运行
call :check_docker_running
if %DOCKER_RUNNING%==0 (
    echo.
    pause
    exit /b 1
)

echo ✅ 环境检查通过

:: ============================================
:: 第二步：创建必要目录
:: ============================================
echo.
echo [2/7] 📁 准备工作目录...
call :create_dirs

:: ============================================
:: 第三步：智能环境配置
:: ============================================
echo.
echo [3/7] ⚙️ 配置部署参数...
call :configure_env

:: ============================================
:: 第四步：显示配置摘要
:: ============================================
echo.
echo [4/7] 📋 当前配置摘要：
echo ┌──────────────────────────────────────────┐
echo │  服务端口:    http://localhost:%SERVER_PORT%           │
echo │  PC端访问:    http://localhost:%SERVER_PORT%/            │
echo │  移动端访问:  http://localhost:%SERVER_PORT%/m/          │
echo │  API地址:     http://localhost:%SERVER_PORT%/api/v1/     │
echo └──────────────────────────────────────────┘
echo.

:: ============================================
:: 第五步：选择操作
:: ============================================
echo [5/7] 🎮 请选择操作：
echo.
echo   1️⃣  🚀 完整部署（构建+启动）- 首次推荐
echo   2️⃣  🔨 仅重建前端（代码更新后）
echo   3️⃣  🔄 重启服务
echo   4️⃣  📊 查看日志
echo   5️⃣  🛑 停止所有服务
echo   6️⃣  🧹 清理重来（删除数据重新部署）
echo   7️⃣  🔧 进入容器终端
echo   8️⃣  🔍 查看服务状态
echo   9️⃣  💾 数据库备份
echo   🔟  🌐 打开浏览器访问
echo   0️⃣  ❌ 退出
echo.
set /p choice="请输入选项 [0-9, 10]: "

if "%choice%"=="1" goto full_deploy
if "%choice%"=="2" goto rebuild_frontend
if "%choice%"=="3" goto restart_services
if "%choice%"=="4" goto view_logs
if "%choice%"=="5" goto stop_all
if "%choice%"=="6" goto clean_rebuild
if "%choice%"=="7" goto shell_access
if "%choice%"=="8" goto check_status
if "%choice%"=="9" goto backup_database
if "%choice%"=="10" goto open_browser
if "%choice%"=="0" goto end_script
echo ❌ 无效选项
pause
exit /b 1

:: ============================================
:: Docker 安装检测函数
:: ============================================
:check_docker
set DOCKER_OK=0

:: 检查 Docker 命令是否可用
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('docker --version') do echo ✅ %%i
    set DOCKER_OK=1
    goto :eof
)

:: Docker 未安装，开始自动安装流程
echo.
echo ╔═══════════════════════════════════════════╗
echo ║   ⚠️ 未检测到 Docker，准备自动安装...     ║
echo ╚═══════════════════════════════════════════╝
echo.

:: 检测系统架构
set ARCH=x86_64
if "%PROCESSOR_ARCHITECTURE%"=="ARM64" set ARCH=aarch64
if "%PROCESSOR_ARCHITEW6432%"=="ARM64" set ARCH=aarch64

echo [信息] 系统架构: %ARCH%
echo.

:: 方式1：尝试使用 winget 安装（Windows 10 1709+）
echo [方式1] 尝试使用 winget 安装...
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ winget 可用
    
    set /p use_winget="是否使用 winget 自动安装 Docker Desktop？[Y/n]: "
    if /i "!use_winget!"=="" set use_winget=Y
    
    if /i "!use_wingent!"=="Y" (
        echo.
        echo 正在通过 winget 安装 Docker Desktop...
        echo 这可能需要几分钟时间，请耐心等待...
        echo.
        
        winget install Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
        
        if %errorlevel% equ 0 (
            echo.
            echo ✅ Docker Desktop 安装成功！
            echo ⏳ 请启动 Docker Desktop 并等待其完全运行后重新运行此脚本
            echo.
            
            :: 尝试自动启动 Docker Desktop
            echo 正在尝试启动 Docker Desktop...
            start "" "C:\Program Files\Docker\Docker Desktop.exe" >nul 2>&1
            
            timeout /t 5 >nul
            echo ✅ Docker Desktop 已启动
            echo ℹ️ 首次启动需要初始化（约1-2分钟），完成后请重新运行此脚本
        ) else (
            echo ❌ winget 安装失败，将尝试其他方式...
        )
    )
)

:: 如果 winget 失败或用户选择否，提供其他安装方式
if %DOCKER_OK%==0 (
    echo.
    echo ┌─────────────────────────────────────────────┐
    echo │         📥 Docker 安装选项                   │
    echo ├─────────────────────────────────────────────┤
    echo │  1. 打开官方下载页面（推荐）                 │
    echo │  2. 使用 Chocolatey 包管理器                │
    echo │  3. 使用 Scoop 包管理器                     │
    echo │  0. 取消                                    │
    echo └─────────────────────────────────────────────┘
    echo.
    set /p install_method="请选择安装方式 [1/2/3/0]: "
    
    if "!install_method!"=="1" (
        echo.
        echo 正在打开 Docker 官方下载页面...
        start https://www.docker.com/products/docker-desktop/
        echo.
        echo 请按以下步骤操作：
        echo   1. 下载 Docker Desktop Installer
        echo   2. 运行安装程序（确保勾选 "Use WSL 2 instead of Hyper-V"）
        echo   3. 安装完成后重启电脑
        echo   4. 启动 Docker Desktop
        echo   5. 等待 Docker 完全启动（托盘图标变稳定）
        echo   6. 重新运行此脚本
        echo.
    )
    
    if "!install_method!"=="2" (
        echo.
        echo 正在检查 Chocolatey...
        where choco >nul 2>&1
        if %errorlevel% neq 0 (
            echoChocolatey 未安装，正在安装...
            powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
        )
        
        echo 正在通过 Chocolatey 安装 Docker Desktop...
        choco install docker-desktop -y
        
        if %errorlevel% equ 0 (
            echo ✅ 安装成功！请启动 Docker Desktop 后重新运行此脚本
            start "" "C:\Program Files\Docker\Docker Desktop.exe"
        )
    )
    
    if "!install_method!"=="3" (
        echo.
        echo 正在检查 Scoop...
        where scoop >nul 2>&1
        if %errorlevel% neq 0 (
            echo Scoop 未安装，正在安装...
            powershell -Command "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser; irm get.scoop.sh | iex"
        )
        
        echo 正在通过 Scoop 安装 Docker...
        scoop install docker
        
        if %errorlevel% equ 0 (
            echo ✅ 安装成功！请手动启动 Docker Desktop 后重新运行此脚本
        )
    )
    
    if "!install_method!"=="0" (
        echo 已取消安装
    )
)

echo.
goto :eof

:: ============================================
:: Docker 运行状态检测
:: ============================================
:check_docker_running
set DOCKER_RUNNING=0

docker info >nul 2>&1
if %errorlevel% equ 0 (
    set DOCKER_RUNNING=1
    goto :eof
)

echo.
echo ⚠️ Docker 已安装但未运行！
echo.

:: 尝试启动 Docker Desktop
set /p try_start="是否尝试启动 Docker Desktop？[Y/n]: "
if /i "!try_start!"=="" set try_start=Y

if /i "!try_start!"=="Y" (
    echo 正在启动 Docker Desktop...
    
    :: 尝试多种可能的路径
    if exist "C:\Program Files\Docker\Docker Desktop.exe" (
        start "" "C:\Program Files\Docker\Docker Desktop.exe"
    ) else if exist "C:\Program Files (x86)\Docker\Docker Desktop.exe" (
        start "" "C:\Program Files (x86)\Docker\Docker Desktop.exe"
    ) else (
        :: 使用 start 命令启动
        start Docker
    )
    
    echo.
    echo ⏳ Docker Desktop 正在启动...
    echo    首次启动可能需要 1-2 分钟初始化
    echo.
    
    :: 等待 Docker 就绪（最多等待120秒）
    set WAIT_COUNT=0
    :wait_loop
    timeout /t 3 >nul
    docker info >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Docker 已就绪！
        set DOCKER_RUNNING=1
        goto :eof
    )
    
    set /a WAIT_COUNT+=3
    if %WAIT_COUNT% lss 120 (
        set /a REMAINING=120-WAIT_COUNT
        echo    等待中... (!REMAINING!秒剩余)
        goto wait_loop
    )
    
    echo.
    echo ❌ Docker 启动超时！
    echo.
    echo 可能的原因：
    echo   1. WSL2 未安装或未启用
    echo   2. Hyper-V 未启用
    echo   3. 系统需要重启
    echo.
    echo 解决方法：
    echo   1. 手动打开 Docker Desktop 查看错误信息
    echo   2. 或以管理员身份运行以下命令启用功能：
    echo      dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    echo      dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    echo      wsl --install
    echo      重启电脑
) else (
    echo 请手动启动 Docker Desktop 后重新运行此脚本
)

goto :eof

:: ============================================
:: 创建目录
:: ============================================
:create_dirs
if not exist "nginx\logs" mkdir nginx\logs >nul 2>&1
if not exist "ssl\certs" mkdir ssl\certs >nul 2>&1
if not exist "backend-v2\sql" mkdir backend-v2\sql >nul 2>&1
if not exist "backend-v2\media" mkdir backend-v2\media >nul 2>&1
if not exist "backend-v2\logs" mkdir backend-v2\logs >nul 2>&1
echo ✅ 目录已就绪
goto :eof

:: ============================================
:: 环境配置
:: ============================================
:configure_env
set NEED_CONFIG=0

:: 检查 .env 文件是否存在且完整
if exist ".env" (
    findstr /C:"change-me" .env >nul 2>&1
    if %errorlevel% equ 0 set NEED_CONFIG=1
    
    findstr /C:"SECRET_KEY=$" .env >nul 2>&1
    if %errorlevel% equ 0 set NEED_CONFIG=1
) else (
    set NEED_CONFIG=1
)

if "%NEED_CONFIG%"=="0" (
    echo ✅ 检测到已有完整配置 (.env)
    
    for /f "tokens=2 delims==" %%a in ('findstr "^SERVER_PORT" .env') do set SERVER_PORT=%%a
    if "!SERVER_PORT!"=="" set SERVER_PORT=80
    
    set /p reuse_config="是否使用现有配置？[Y/n]: "
    if /i "!reuse_config!"=="n" set NEED_CONFIG=1
)

if "%NEED_CONFIG%"=="1" call :generate_env

:: 读取配置用于显示
for /f "tokens=2 delims==" %%a in ('findstr "^SERVER_PORT" .env') do set SERVER_PORT=%%a
if "!SERVER_PORT!"=="" set SERVER_PORT=80
goto :eof

:: ============================================
:: 生成环境配置
:: ============================================
:generate_env
echo.
echo ┌─────────────────────────────────────┐
echo │     🎯 首次部署配置向导              │
echo │     (跟着提示输入即可，支持回车跳过) │
echo └─────────────────────────────────────┘
echo.

:: 生成 Django SECRET_KEY
echo [密钥] 正在生成 Django 安全密钥...
for /f %%i in ('python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2^>nul') do set DJANGO_KEY=%%i
if "!DJANGO_KEY!"=="" (
    for /f %%i in ('powershell -Command "[System.Guid]::NewGuid().ToString('N')"') do set DJANGO_KEY=%%i
)
echo ✅ 密钥已生成: !DJANGO_KEY:~0,20!...

set /p SECRET_KEY="Django密钥 [自动生成]: "
if "!SECRET_KEY!"=="" set SECRET_KEY=!DJANGO_KEY!

echo.
:: 数据库密码
set /p DB_PASSWORD="数据库密码 [lims2024secure]: "
if "!DB_PASSWORD!"=="" set DB_PASSWORD=lims2024secure

set /p DB_ROOT_PASSWORD="MySQL Root密码 [root2024secure]: "
if "!DB_ROOT_PASSWORD!"=="" set DB_ROOT_PASSWORD=root2024secure

echo.
:: 加密密钥（32位）
echo [加密] 正在生成密码加密密钥...
for /f %%i in ('powershell -Command "-join ((65..90)+(97..122)+(48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})"') do set ENCRYPT_KEY=%%i
echo ✅ 加密密钥已生成: !ENCRYPT_KEY:~0,16!...

set /p PASSWORD_ENCRYPT_KEY="密码加密密钥(32位) [自动生成]: "
if "!PASSWORD_ENCRYPT_KEY!"=="" set PASSWORD_ENCRYPT_KEY=!ENCRYPT_KEY!

echo.
:: 服务器端口
set /p SERVER_PORT="服务端口 [8080]: "
if "!SERVER_PORT!"=="" set SERVER_PORT=8080

:: 服务器IP地址（用于跨域访问）
echo [IP] 检测本机IP地址...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1"') do set LAN_IP=%%a
set LAN_IP=!LAN_IP: =!
if "!LAN_IP!"=="" set LAN_IP=192.168.1.100
echo ✅ 检测到IP: !LAN_IP!

set /p SERVER_IP="服务器IP地址(手机/外网访问用) [!LAN_IP!]: "
if "!SERVER_IP!"=="" set SERVER_IP=!LAN_IP!

:: 允许的主机
set /p ALLOWED_HOSTS="允许的域名(逗号分隔) [*]: "
if "!ALLOWED_HOSTS!"=="" set ALLOWED_HOSTS=*

echo.
:: DeepSeek AI（可选）
set /p DEEPSEEK_API_KEY="DeepSeek API Key [跳过]: "

:: 写入 .env 文件
echo.
echo [保存] 正在生成 .env 配置文件...
(
    echo # LIMS 环境配置 - 由部署脚本自动生成
    echo # 生成时间: %date% %time%
    echo.
    echo # ── Django 后端 ──
    echo SECRET_KEY=%SECRET_KEY%
    echo ALLOWED_HOSTS=%ALLOWED_HOSTS%
    echo CORS_ALLOWED_ORIGINS=*
    echo PASSWORD_ENCRYPT_KEY=%PASSWORD_ENCRYPT_KEY%
    echo SERVER_IP=%SERVER_IP%
    echo.
    echo # ── 前端构建变量 ^(VITE_ 前缀^) ──
    echo VITE_PASSWORD_ENCRYPT_KEY=%PASSWORD_ENCRYPT_KEY%
    echo VITE_API_V2_BASE_URL=/api/v1
    echo.
    echo # ── MySQL 数据库 ──
    echo DB_NAME=lims
    echo DB_USER=lims
    echo DB_PASSWORD=%DB_PASSWORD%
    echo DB_ROOT_PASSWORD=%DB_ROOT_PASSWORD%
    echo.
    echo # ── 服务端口 ──
    echo SERVER_PORT=%SERVER_PORT%
    echo HTTPS_PORT=443
    echo.
    echo # ── AI 功能 ^(可选^) ──
    echo DEEPSEEK_API_KEY=%DEEPSEEK_API_KEY%
    echo DEEPSEEK_SERVICE_URL=https://api.deepseek.com/v1/chat/completions
    echo DEEPSEEK_MODEL=deepseek-chat
) > .env
echo ✅ 配置已保存到 .env (共13项配置)
goto :eof

:: ============================================
:: 功能实现
:: ============================================

:full_deploy
echo.
echo ════════════════════════════════════════════
echo   🚀 开始完整部署...
echo ════════════════════════════════════════════
echo.

echo [1/4] 🛑 停止旧容器...
docker-compose down --remove-orphans 2>nul

echo [2/4] 🏗️ 构建镜像（首次需要几分钟，请耐心等待）...
echo     ├─ 构建 PC端前端...
docker-compose build --no-cache frontend-pc 2>nul
if %errorlevel% neq 0 (
    echo ❌ PC端构建失败！
    docker-compose logs frontend-pc
    pause
    exit /b 1
)
echo     ✅ PC端完成
echo     ├─ 构建移动端前端...
docker-compose build --no-cache frontend-mobile 2>nul
if %errorlevel% neq 0 (
    echo ❌ 移动端构建失败！
    docker-compose logs frontend-mobile
    pause
    exit /b 1
)
echo     ✅ 移动端完成
echo     ├─ 构建后端服务...
docker-compose build --no-cache backend 2>nul
if %errorlevel% neq 0 (
    echo ❌ 后端构建失败！
    docker-compose logs backend
    pause
    exit /b 1
)
echo     ✅ 后端完成

echo [3/4] 🚢 启动所有服务...
docker-compose up -d 2>nul
if %errorlevel% neq 0 (
    echo ❌ 启动失败！
    docker-compose logs
    pause
    exit /b 1
)

echo [4/4] ⏳ 等待服务就绪...
call :wait_for_service 30

goto show_status

:rebuild_frontend
echo.
echo ════════════════════════════════════════════
echo   🔨 重新构建前端...
echo ════════════════════════════════════════════
echo.
docker-compose build --no-cache frontend-pc frontend-mobile
docker-compose up -d nginx
call :wait_for_service 10
goto show_status

:restart_services
echo.
echo ════════════════════════════════════════════
echo   🔄 重启服务...
echo ════════════════════════════════════════════
docker-compose restart
call :wait_for_service 10
goto show_status

:view_logs
echo.
echo 请选择要查看的服务日志：
echo   1. 全部服务
echo   2. 后端 (Django)
echo   3. Nginx (反向代理)
echo   4. 数据库 (MySQL)
echo   5. Redis (缓存)
echo   6. PC端构建
echo   7. 移动端构建
echo   0. 返回
echo.
set /p log_choice="选择 [0-7]: "

if "%log_choice%"=="1" docker-compose logs -f --tail=100 & goto end_script
if "%log_choice%"=="2" docker-compose logs -f --tail=100 backend & goto end_script
if "%log_choice%"=="3" docker-compose logs -f --tail=100 nginx & goto end_script
if "%log_choice%"=="4" docker-compose logs -f --tail=100 db & goto end_script
if "%log_choice%"=="5" docker-compose logs -f --tail=100 redis & goto end_script
if "%log_choice%"=="6" docker-compose logs -f --tail=100 frontend-pc & goto end_script
if "%log_choice%"=="7" docker-compose logs -f --tail=100 frontend-mobile & goto end_script
if "%log_choice%"=="0" goto end_script
docker-compose logs -f --tail=100 & goto end_script

:stop_all
echo.
echo ════════════════════════════════════════════
echo   🛑 停止所有服务...
echo ════════════════════════════════════════════
docker-compose down
echo.
echo ✅ 所有服务已停止
echo 💡 提示: 数据库数据已保留，下次启动不会丢失
pause
exit /b 0

:clean_rebuild
echo.
echo ════════════════════════════════════════════
echo   ⚠️ 警告：此操作将删除所有数据！
echo ════════════════════════════════════════════
echo.
set /p confirm="确定要清理并完全重新部署吗？(y/N): "
if /i not "%confirm%"=="y" (
    echo 已取消
    pause
    exit /b 0
)

echo.
echo [清理] 删除容器、镜像和数据卷...
docker-compose down -v --remove-orphans
docker system prune -af

echo [重建] 重新构建并启动...
docker-compose build --no-cache
docker-compose up -d
call :wait_for_service 30
goto show_status

:shell_access
echo.
echo 请选择要进入的容器：
echo   1. 后端 (Django)
echo   2. 数据库 (MySQL)
echo   3. Redis
echo   4. Nginx
echo   0. 返回
echo.
set /p shell_choice="选择 [0-4]: "

if "%shell_choice%"=="1" docker exec -it lims_backend bash & goto end_script
if "%shell_choice%"=="2" docker exec -it lims_db mysql -u root -p%DB_ROOT_PASSWORD% lims & goto end_script
if "%shell_choice%"=="3" docker exec -it lims_redis redis-cli & goto end_script
if "%shell_choice%"=="4" docker exec -it lims_nginx sh & goto end_script
if "%shell_choice%"=="0" goto end_script
goto end_script

:check_status
echo.
echo ════════════════════════════════════════════
echo   📊 服务运行状态
echo ════════════════════════════════════════════
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ════════════════════════════════════════════
echo   💻 资源占用情况
echo ════════════════════════════════════════════
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
pause
exit /b 0

:backup_database
echo.
echo ════════════════════════════════════════════
echo   💾 数据库备份
echo ════════════════════════════════════════════
echo.

if not exist "backups" mkdir backups

for /f "tokens=2 delims==" %%a in ('findstr "^DB_ROOT_PASSWORD" .env') do set BACKUP_PASS=%%a

set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%%time:~0,2%%time:~3,2
set BACKUP_FILE=backups\lims_backup_%TIMESTAMP%.sql

echo 正在备份数据库到: %BACKUP_FILE%

docker exec lims_db mysqldump -u root -p%BACKUP_PASS% lims > "%BACKUP_FILE%" 2>nul

if %errorlevel% equ 0 (
    echo ✅ 备份完成: %BACKUP_FILE%
    
    :: 显示文件大小
    for %%A in ("%BACKUP_FILE%") do set size=%%~zA
    set /a sizeMB=!size!/1048576
    echo 📊 文件大小: 约 !sizeMB! MB
    
    :: 清理旧备份（保留最近7个）
    for /f "skip=7 delims=" %%F in ('dir /b /o-d backups\*.sql 2^>nul') do del "backups\%%F" 2>nul
    echo 🧹 已清理旧备份（保留最近7个）
) else (
    echo ❌ 备份失败！请检查数据库连接
)

pause
exit /b 0

:open_browser
echo.
echo ════════════════════════════════════════════
echo   🌐 打开浏览器访问
echo ════════════════════════════════════════════
echo.

echo 选择要打开的页面：
echo   1. PC端首页
echo   2. 移动端首页
echo   3. API文档（如果有）
echo   0. 返回
echo.
set /p browser_choice="选择 [0-3]: "

if "%browser_choice%"=="1" start http://localhost:%SERVER_PORT%/ & goto end_script
if "%browser_choice%"=="2" start http://localhost:%SERVER_PORT%/m/ & goto end_script
if "%browser_choice%"=="3" start http://localhost:%SERVER_PORT%/api/v1/ & goto end_script
if "%browser_choice%"=="0" goto end_script
goto end_script

:: ============================================
:: 显示最终状态
:: ============================================
:show_status
echo.
echo ════════════════════════════════════════════
echo   📊 服务运行状态
echo ════════════════════════════════════════════
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ════════════════════════════════════════════
echo   ✅ 部署完成！
echo ════════════════════════════════════════════
echo.
echo 🌐 访问地址：
echo    ┌────────────────────────────────────┐
echo    │  🖥️ PC端:  http://localhost:%SERVER_PORT%/      │
echo    │  📱 移动端: http://localhost:%SERVER_PORT%/m/    │
echo    │  🔌 API:   http://localhost:%SERVER_PORT%/api/v1/│
echo    │  ❤️ 健康:  http://localhost:%SERVER_PORT%/health │
echo    └────────────────────────────────────┘
echo.
echo 📝 默认账号（如果有初始化数据）：
echo    用户名: admin
echo    密码: admin123
echo.
echo 🔧 常用命令：
echo    查看日志: deploy.bat → 选择 4
echo    重启服务: deploy.bat → 选择 3
echo    停止服务: deploy.bat → 选择 5
echo    数据库备份: deploy.bat → 选择 9
echo    打开浏览器: deploy.bat → 选择 10
echo.
echo 📖 详细文档: DEPLOY.md (Windows) / DEPLOY_LINUX.md (Linux)
echo.

:: 检测局域网IP（方便手机访问）
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1"') do set LAN_IP=%%a
if defined LAN_IP (
    echo 📱 局域网访问（手机同WiFi下）:
    echo    PC端:  http://%LAN_IP%:%SERVER_PORT%/
    echo    移动端: http://%LAN_IP%:%SERVER_PORT%/m/
    echo.
)

:: 询问是否打开浏览器
set /p open_browser="是否现在打开浏览器？[Y/n]: "
if /i "!open_browser!"=="" set open_browser=Y
if /i "!open_browser!"=="Y" (
    echo 正在打开浏览器...
    start http://localhost:%SERVER_PORT%/
)

pause
exit /b 0

:end_script
echo.
echo 再见！👋
pause
exit /b 0

:: ============================================
:: 子程序：等待服务启动
:: ============================================
:wait_for_service
echo ⏳ 等待服务启动（最多 %1 秒）...
timeout /t %1 >nul
goto :eof