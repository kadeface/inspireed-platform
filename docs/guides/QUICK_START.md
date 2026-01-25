# 快捷启动指南

## 🚀 快速启动方式

### 方式一：双击启动文件（推荐）

项目根目录中有两个启动文件，双击即可启动：

1. **`启动InspireEd.command`** ⭐ 推荐
   - 双击后会在终端中打开并启动服务
   - 启动完成后窗口会保持打开，显示服务状态
   - 关闭窗口不会停止服务

2. **`启动InspireEd.sh`**
   - 双击后会在新终端窗口中启动服务
   - 适合快速启动

### 方式二：创建桌面快捷方式

运行以下命令在桌面创建快捷方式：

```bash
./scripts/create-desktop-shortcut.sh
```

然后就可以在桌面双击 "启动InspireEd.command" 来启动服务了。

### 方式三：使用终端命令

```bash
# 进入项目目录
cd /Users/zhangxixi/cursor-project/InspireEd/inspireed-platform

# 启动服务
./start.sh
```

### 方式四：使用别名（添加到 ~/.zshrc）

```bash
# 编辑 ~/.zshrc
nano ~/.zshrc

# 添加以下行
alias inspireed-start='cd /Users/zhangxixi/cursor-project/InspireEd/inspireed-platform && ./start.sh'
alias inspireed-stop='cd /Users/zhangxixi/cursor-project/InspireEd/inspireed-platform && ./stop.sh'
alias inspireed-restart='cd /Users/zhangxixi/cursor-project/InspireEd/inspireed-platform && ./restart.sh'

# 重新加载配置
source ~/.zshrc

# 然后就可以在任何地方使用：
inspireed-start
inspireed-stop
inspireed-restart
```

## 📋 文件说明

- `启动InspireEd.command` - macOS 可执行脚本，双击运行
- `启动InspireEd.sh` - Shell 脚本，双击运行
- `start.sh` - 主启动脚本
- `stop.sh` - 停止服务脚本
- `restart.sh` - 重启服务脚本

## 🔍 检查服务状态

```bash
# 检查后端服务
curl http://localhost:8000/health

# 检查前端服务
curl http://localhost:5173

# 查看进程
ps aux | grep uvicorn
ps aux | grep "pnpm dev"
```

## 🛑 停止服务

```bash
# 方式一：使用停止脚本
./stop.sh

# 方式二：手动停止
# 查找进程 ID
ps aux | grep uvicorn | grep -v grep
ps aux | grep "pnpm dev" | grep -v grep

# 停止进程（替换 PID 为实际进程 ID）
kill <PID>
```

## 💡 提示

1. **首次启动**：可能需要 1-2 分钟来启动所有服务
2. **Docker 要求**：确保 Docker Desktop 已启动
3. **端口占用**：如果端口被占用，服务可能无法启动
4. **查看日志**：启动过程中的日志会显示在终端中

## 🐛 故障排查

### 问题：双击文件没有反应

**解决方案：**
1. 右键点击文件 → "打开方式" → 选择 "终端"
2. 或者在终端中运行：
   ```bash
   chmod +x 启动InspireEd.command
   ./启动InspireEd.command
   ```

### 问题：提示权限不足

**解决方案：**
```bash
chmod +x 启动InspireEd.command
chmod +x start.sh
```

### 问题：Docker 未启动

**解决方案：**
1. 打开 Docker Desktop
2. 确保 Docker Desktop 已设置为开机自动启动
3. 等待 Docker 完全启动后再运行启动脚本

### 问题：端口被占用

**解决方案：**
```bash
# 检查端口占用
lsof -i :8000  # 后端端口
lsof -i :5173  # 前端端口

# 停止占用端口的进程
kill <PID>
```

## 📱 访问地址

启动成功后，可以通过以下地址访问：

- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 🔄 自动启动设置

如果需要系统启动时自动启动服务，请运行：

```bash
./scripts/install-autostart.sh
```

详细说明请查看 `AUTOSTART_FIX.md`

