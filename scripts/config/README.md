# 脚本配置文件

本目录包含脚本使用的配置文件模板。

## 文件说明

### `com.inspireed.plist`
macOS LaunchAgent 配置文件模板。用于配置系统自动启动服务。

**使用方式：**
- 通过 `scripts/install-autostart.sh` 脚本安装
- 脚本会自动将 `PROJECT_PATH` 替换为实际项目路径
- 安装后的文件会复制到 `~/Library/LaunchAgents/` 目录

**注意：** 此文件已从根目录移动到此目录，相关脚本已更新路径引用。
