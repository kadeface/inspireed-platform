# ⚠️ 重要提示：后端进程管理

## 问题

在修复过程中发现**旧的后端进程（PID 4208）仍在运行**，导致：
- 修改的代码没有生效
- 仍然发送 `teacher_disconnected` 消息
- 自动结束会话逻辑未被禁用

## 根本原因

后端使用 `uvicorn --reload` 模式启动，但：
1. **多次启动**导致多个进程同时运行
2. **PID文件不准确**（记录的是新进程，但旧进程还在运行）
3. 旧进程占用端口，导致代码更新不生效

## 解决方案

### 1. 清理所有旧进程

```bash
# 查找所有 uvicorn 进程
ps aux | grep uvicorn | grep -v grep

# 停止所有进程
pkill -f uvicorn

# 或者手动停止特定PID
kill 4208
```

### 2. 确认端口被释放

```bash
# 检查8000端口
lsof -i :8000 | grep LISTEN

# 如果有进程，记下PID并停止
kill <PID>
```

### 3. 重新启动后端

```bash
cd backend
source venv/bin/activate
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
echo $! > ../logs/backend.pid
```

### 4. 验证新进程

```bash
# 检查健康状态
curl http://localhost:8000/health

# 确认PID一致
cat logs/backend.pid
lsof -i :8000 | grep LISTEN
```

## 建议的启动脚本改进

修改 `start.sh` 以防止多进程问题：

```bash
# 在启动新进程前，先停止旧进程
if [ -f "logs/backend.pid" ]; then
    OLD_PID=$(cat logs/backend.pid)
    if kill -0 $OLD_PID 2>/dev/null; then
        echo "停止旧的后端进程 (PID: $OLD_PID)..."
        kill $OLD_PID
        sleep 2
    fi
fi

# 确保端口被释放
if lsof -i :8000 > /dev/null 2>&1; then
    echo "❌ 端口8000仍被占用，请手动清理"
    lsof -i :8000
    exit 1
fi

# 启动新进程
...
```

## 当前状态

✅ **已修复**：
- 停止了旧进程（PID 4208）
- 启动了新进程（PID 68305）
- 最新代码已生效
- 自动结束逻辑已被禁用

## 测试步骤

1. **重新测试激活活动模块**
2. **验证不再误报"课程已结束"**
3. **确认教师 WebSocket 断开不会自动结束会话**

---

**修复时间**：2025-11-30  
**问题**：旧后端进程未停止，代码更新不生效  
**解决**：清理旧进程，重启后端服务

