# 其他脚本目录

本目录包含项目中的其他 Shell 脚本文件，这些脚本不是核心启动/停止脚本。

## 文件说明

### `start-prod.sh`
生产环境启动脚本。

### `stop-prod.sh`
生产环境停止脚本。

### `start-cloudstudio.sh`
CloudStudio 环境启动脚本。

### `check-logs.sh`
日志检查脚本。

### `启动InspireEd.sh`
中文命名的启动脚本。

## 使用方法

如果需要使用这些脚本，可以：

1. **直接运行**：
   ```bash
   cd scripts/other
   ./start-prod.sh
   ```

2. **复制到根目录**（如果需要频繁使用）：
   ```bash
   cp scripts/other/start-prod.sh .
   ```

3. **创建符号链接**（推荐）：
   ```bash
   ln -s scripts/other/start-prod.sh start-prod.sh
   ```

## 注意

- 核心启动脚本（`start.sh`, `stop.sh`, `restart.sh`）保留在项目根目录，便于直接使用
- 其他脚本按需使用，可以从此目录运行或复制到根目录
