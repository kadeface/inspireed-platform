# Docker 自动启动配置指南

本文档说明如何配置 Docker 容器在系统启动时自动启动。

## 📋 自动启动方式

### 方式一：Docker Compose Restart 策略（推荐）

已在 `docker-compose.yml` 和 `docker-compose.prod.yml` 中为所有服务配置了 `restart: unless-stopped` 策略。

**说明：**
- `restart: unless-stopped`：容器会在 Docker 守护进程启动时自动启动，除非容器被手动停止
- `restart: always`：容器总是自动重启（即使被手动停止）
- `restart: on-failure`：只在容器异常退出时重启

**当前配置：**
所有服务（PostgreSQL、Redis、MinIO、Kafka、Zookeeper）都已配置为 `restart: unless-stopped`。

**验证配置：**
```bash
cd docker
docker-compose ps
# 查看所有容器的状态，应该显示 "Up" 状态
```

### 方式二：macOS - Docker Desktop 自动启动

#### 1. 设置 Docker Desktop 开机自启

1. 打开 **Docker Desktop** 应用
2. 点击右上角的 **设置（Settings）** 图标
3. 在左侧菜单选择 **General**
4. 勾选 **"Start Docker Desktop when you log in"**（登录时自动启动 Docker Desktop）
5. 点击 **Apply & Restart**

#### 2. 验证 Docker Desktop 自动启动

重启 Mac，登录后检查：
```bash
docker info
# 如果显示 Docker 信息，说明 Docker Desktop 已自动启动
```

### 方式三：macOS - 使用 LaunchAgent（系统级自动启动）

如果你希望系统启动时自动启动 Docker Compose 服务，可以使用 LaunchAgent。

#### 1. 创建 Docker 自动启动脚本

```bash
# 创建脚本目录
mkdir -p ~/Library/LaunchAgents

# 创建启动脚本
cat > ~/Library/LaunchAgents/com.inspireed.docker.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.inspireed.docker</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd /Users/zhangxixi/cursor-project/InspireEd/inspireed-platform/docker && docker-compose up -d</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/zhangxixi/cursor-project/InspireEd/inspireed-platform</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/Users/zhangxixi/cursor-project/InspireEd/inspireed-platform/logs/docker-autostart.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/zhangxixi/cursor-project/InspireEd/inspireed-platform/logs/docker-autostart.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin</string>
    </dict>
</dict>
</plist>
EOF
```

**注意：** 请将路径 `/Users/zhangxixi/cursor-project/InspireEd/inspireed-platform` 替换为你的实际项目路径。

#### 2. 加载 LaunchAgent

```bash
# 加载服务
launchctl load ~/Library/LaunchAgents/com.inspireed.docker.plist

# 立即启动（测试）
launchctl start com.inspireed.docker

# 查看状态
launchctl list | grep com.inspireed.docker
```

#### 3. 卸载 LaunchAgent（如需要）

```bash
# 停止服务
launchctl stop com.inspireed.docker

# 卸载服务
launchctl unload ~/Library/LaunchAgents/com.inspireed.docker.plist

# 删除配置文件
rm ~/Library/LaunchAgents/com.inspireed.docker.plist
```

### 方式四：Linux - 使用 systemd（适用于 Linux 服务器）

#### 1. 创建 systemd 服务文件

```bash
sudo nano /etc/systemd/system/inspireed-docker.service
```

#### 2. 添加以下内容

```ini
[Unit]
Description=InspireEd Docker Services
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/inspireed-platform/docker
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

**注意：** 请将 `/path/to/inspireed-platform` 替换为你的实际项目路径。

#### 3. 启用并启动服务

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable inspireed-docker.service

# 启动服务
sudo systemctl start inspireed-docker.service

# 查看状态
sudo systemctl status inspireed-docker.service
```

## 🔍 验证自动启动

### 1. 检查容器状态

```bash
cd docker
docker-compose ps
```

所有容器应该显示为 "Up" 状态。

### 2. 测试重启

```bash
# 重启系统或 Docker Desktop
# 然后检查容器是否自动启动
docker-compose ps
```

### 3. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f postgres
docker-compose logs -f redis
```

## 🛠️ 常用命令

### 启动服务
```bash
cd docker
docker-compose up -d
```

### 停止服务
```bash
cd docker
docker-compose down
```

### 重启服务
```bash
cd docker
docker-compose restart
```

### 查看服务状态
```bash
cd docker
docker-compose ps
```

### 查看服务日志
```bash
cd docker
docker-compose logs -f [service_name]
```

## ⚠️ 注意事项

1. **Docker Desktop 必须先启动**：容器自动启动的前提是 Docker Desktop 或 Docker 守护进程正在运行。

2. **端口冲突**：如果端口被占用，容器可能无法启动。检查端口占用：
   ```bash
   # macOS
   lsof -i :5432
   lsof -i :6379
   
   # Linux
   netstat -tlnp | grep 5432
   ```

3. **数据持久化**：使用 Docker volumes 确保数据持久化，即使容器重启数据也不会丢失。

4. **资源限制**：确保系统有足够的资源（内存、CPU）运行所有容器。

5. **网络问题**：如果容器无法启动，检查 Docker 网络：
   ```bash
   docker network ls
   docker network inspect docker_default
   ```

## 📚 相关文档

- [Docker Compose 官方文档](https://docs.docker.com/compose/)
- [Docker Restart 策略](https://docs.docker.com/config/containers/start-containers-automatically/)
- [macOS LaunchAgent 文档](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
- [Linux systemd 文档](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

