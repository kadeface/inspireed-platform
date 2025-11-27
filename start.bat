@echo off
chcp 65001 >nul
echo 🚀 启动 InspireEd 教师教研系统...

REM 检查 Docker 是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未运行，请先启动 Docker Desktop
    pause
    exit /b 1
)

REM 启动基础服务
echo 📦 启动基础服务 (PostgreSQL, Redis, MinIO, Kafka)...
cd docker
docker-compose up -d
if errorlevel 1 (
    echo ❌ Docker 服务启动失败
    cd ..
    pause
    exit /b 1
)
cd ..

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 5 /nobreak >nul

REM 检查服务状态
echo 🔍 检查服务状态...
docker-compose -f docker\docker-compose.yml ps

REM 启动后端服务
echo 🔧 启动后端服务...
cd backend

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建 Python 虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Python 虚拟环境创建失败，请检查 Python 是否已安装
        cd ..
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装后端依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    cd ..
    pause
    exit /b 1
)

REM 创建环境配置
if not exist ".env" (
    echo ⚙️ 创建环境配置文件...
    copy env.example .env >nul
)

REM 运行数据库迁移
echo 🗄️ 运行数据库迁移...
alembic upgrade head
if errorlevel 1 (
    echo ⚠️ 数据库迁移失败，请检查数据库连接
)

REM 创建日志目录
if not exist "..\logs" mkdir ..\logs

REM 启动后端服务（后台运行）
echo 🚀 启动后端服务 (端口 8000)...
start "InspireEd Backend" /min cmd /c "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ..\logs\backend.log 2>&1"

cd ..

REM 等待后端启动
echo ⏳ 等待后端服务启动...
timeout /t 3 /nobreak >nul

REM 检查后端健康状态
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 后端服务可能未启动，请检查日志: logs\backend.log
) else (
    echo ✅ 后端服务启动成功
)

REM 启动前端服务
echo 🎨 启动前端服务...
cd frontend

REM 安装依赖
echo 📥 安装前端依赖...
if not exist "node_modules" (
    pnpm install
    if errorlevel 1 (
        echo ❌ 前端依赖安装失败
        cd ..
        pause
        exit /b 1
    )
)

REM 创建环境配置
if not exist ".env.local" (
    echo ⚙️ 创建前端环境配置文件...
    copy env.example .env.local >nul
)

REM 启动前端服务（后台运行）
echo 🚀 启动前端服务 (端口 5173)...
start "InspireEd Frontend" /min cmd /c "pnpm dev > ..\logs\frontend.log 2>&1"

cd ..

REM 等待前端启动
echo ⏳ 等待前端服务启动...
timeout /t 5 /nobreak >nul

REM 获取本机 IP 地址
setlocal enabledelayedexpansion
set LOCAL_IP=
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i /c:"IPv4"') do (
    set "LOCAL_IP=%%a"
    set "LOCAL_IP=!LOCAL_IP: =!"
    if not "!LOCAL_IP!"=="" (
        if not "!LOCAL_IP!"=="127.0.0.1" (
            goto :ip_found
        )
    )
)
:ip_found
if defined LOCAL_IP (
    endlocal & set LOCAL_IP=%LOCAL_IP%
) else (
    endlocal
)

echo.
echo 🎉 服务启动完成！
echo.
echo 📱 访问地址：
echo.
echo    【本机访问】
echo    前端应用: http://localhost:5173
echo    后端API: http://localhost:8000
echo    API文档: http://localhost:8000/docs

if defined LOCAL_IP (
    if not "%LOCAL_IP%"=="" (
        echo.
        echo    【局域网访问】（其他设备使用这些地址）
        echo    前端应用: http://%LOCAL_IP%:5173
        echo    后端API: http://%LOCAL_IP%:8000
        echo    API文档: http://%LOCAL_IP%:8000/docs
        echo.
        echo    💡 提示：
        echo    - 确保设备连接到同一局域网
        echo    - 防火墙需允许 5173 和 8000 端口
        echo    - 移动设备可访问: http://%LOCAL_IP%:5173
    )
)

echo.
echo 🔐 测试账号：
echo    管理员: admin@inspireed.com / admin123
echo    教师: teacher@inspireed.com / teacher123
echo    学生: student@inspireed.com / student123
echo    研究员: researcher@inspireed.com / researcher123
echo.
echo 📋 管理命令：
echo    查看日志: type logs\backend.log 或 type logs\frontend.log
echo    停止服务: stop.bat
echo    重启服务: restart.bat
echo.
echo ✨ 开始使用 InspireEd 吧！
echo.
pause

