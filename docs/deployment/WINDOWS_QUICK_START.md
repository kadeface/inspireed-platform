# Windows 快速开始指南

这是 Windows 系统上最简单的部署方法，只需 3 步即可启动系统。

## ⚡ 超快速开始（3 步）

### 第 1 步：安装必需软件

1. **Docker Desktop for Windows**
   - 下载：https://www.docker.com/products/docker-desktop/
   - 安装后启动 Docker Desktop

2. **Python 3.10+**
   - 下载：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

3. **Node.js 18+**
   - 下载：https://nodejs.org/
   - 安装后运行：`npm install -g pnpm`

### 第 2 步：启动 Docker Desktop

确保 Docker Desktop 正在运行（系统托盘有 Docker 图标）

### 第 3 步：运行启动脚本

双击运行项目根目录下的 `start.bat`，或打开 PowerShell/CMD 运行：

```cmd
start.bat
```

等待脚本自动完成所有配置和启动（约 2-3 分钟）

## ✅ 完成！

访问以下地址：

- **前端应用**：http://localhost:5173
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

## 🔐 测试账号

- 管理员：admin@inspireed.com / admin123
- 教师：teacher@inspireed.com / teacher123
- 学生：student@inspireed.com / student123

## 🛑 停止服务

运行 `stop.bat` 或双击 `stop.bat` 文件

## 📚 更多信息

- 详细部署指南：[Windows 部署指南](./WINDOWS_DEPLOYMENT_GUIDE.md)
- 常见问题：查看部署指南中的"常见问题"部分
- 局域网访问：查看部署指南中的"局域网访问配置"部分

---

**就是这么简单！** 🎉

