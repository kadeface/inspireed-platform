@echo off
chcp 65001 >nul
echo 🔄 重启 InspireEd 教师教研系统...

echo 1️⃣ 停止现有服务...
call stop.bat

echo.
echo 2️⃣ 启动服务...
call start.bat

