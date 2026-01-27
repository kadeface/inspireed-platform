#!/bin/bash

# 防止 Mac 进入睡眠模式
# 运行此脚本可以保持系统唤醒状态

echo "🔒 防止系统进入睡眠模式..."
echo "按 Ctrl+C 停止"
echo ""

# caffeinate 命令可以防止系统睡眠
# -d: 防止显示器睡眠
# -i: 防止系统空闲睡眠
caffeinate -dis

