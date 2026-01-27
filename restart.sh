#!/bin/bash

echo "🔄 重启 InspireEd 教师教研系统..."

# 停止服务
./stop.sh

# 等待服务完全停止
echo "⏳ 等待服务完全停止..."
sleep 3

# 启动服务
./start.sh
