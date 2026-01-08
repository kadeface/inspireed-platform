# 🔇 快速关闭调试日志

## 立即关闭所有调试日志

编辑 `frontend/.env.local` 文件：

```bash
# 将此行设置为 false
VITE_ENABLE_DEBUG_LOGS=false
```

然后重启前端开发服务器：

```bash
# 按 Ctrl+C 停止当前服务器
# 然后重新启动
npm run dev
```

## 验证是否生效

打开浏览器控制台，如果看不到带有表情符号（📥 💾 ✅ 🔍）的调试日志，说明已成功关闭。

**注意：** 错误日志（❌）仍然会显示，这是为了帮助诊断问题。

## 部署到生产环境

生产环境自动使用 `.env.production` 配置，调试日志已默认关闭。

构建生产版本：
```bash
npm run build
```

## 需要临时开启调试？

修改 `.env.local`：
```bash
VITE_ENABLE_DEBUG_LOGS=true
VITE_LOG_LEVEL=DEBUG
```

仅调试特定模块：
```bash
VITE_ENABLE_DEBUG_LOGS=true
VITE_DEBUG_MODULES=API,WEBSOCKET
```

更多详细配置请参考 [DEBUG_LOGS_GUIDE.md](./DEBUG_LOGS_GUIDE.md)
