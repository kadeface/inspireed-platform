@echo off
chcp 65001 >nul
echo 🛑 停止 InspireEd 教师教研系统...

REM 停止前端服务
echo 🎨 停止前端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM 停止后端服务
echo 🔧 停止后端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM 停止 Docker 服务
echo 📦 停止 Docker 服务...
cd docker
docker-compose down
cd ..

echo.
echo ✅ 所有服务已停止
echo.
pause

