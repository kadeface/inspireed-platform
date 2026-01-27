# CloudStudio Preview 启动信息查看指南

## 问题

在 CloudStudio 中使用 `.vscode/preview.yml` 启动应用时，可能看不到启动脚本的输出信息。

## 原因

CloudStudio 的预览功能可能不会实时显示所有标准输出，特别是：
1. 输出被缓冲，没有立即刷新
2. 预览面板只显示部分输出
3. 某些输出被重定向到日志文件

## 解决方案

### 方法一：查看 CloudStudio 终端输出

1. **打开 CloudStudio 终端**：
   - 点击 CloudStudio 界面底部的"终端"标签
   - 或使用快捷键：`Ctrl+`` (Windows/Linux) 或 `Cmd+`` (Mac)

2. **查看启动日志**：
   ```bash
   # 查看后端启动日志
   tail -f /tmp/backend-startup.log
   
   # 查看前端启动日志
   tail -f /tmp/frontend-startup.log
   ```

### 方法二：在预览面板中查看

1. **打开预览面板**：
   - 点击 CloudStudio 右侧的"预览"按钮
   - 或使用快捷键：`Ctrl+Shift+P` 然后输入 "Preview"

2. **查看应用状态**：
   - 预览面板会显示应用的运行状态
   - 如果应用正在启动，会显示"启动中..."
   - 如果应用已启动，会显示访问地址

### 方法三：手动运行启动脚本

如果想看到完整的启动输出，可以手动运行启动脚本：

```bash
# 启动后端
bash .vscode/start-backend-cloudstudio.sh

# 启动前端（在另一个终端）
bash .vscode/start-frontend-cloudstudio.sh
```

### 方法四：检查服务状态

```bash
# 检查后端服务是否运行
curl http://localhost:8000/health

# 检查前端服务是否运行
curl http://localhost:5173

# 查看端口占用情况
lsof -i :8000  # 后端
lsof -i :5173  # 前端
```

## 启动脚本优化

我已经优化了启动脚本，添加了：

1. **清晰的输出分隔线**：
   ```
   ==========================================
   🚀 InspireEd 后端服务启动中...
   ==========================================
   ```

2. **状态信息**：
   - 显示服务地址
   - 显示 API 文档地址
   - 显示健康检查地址

3. **输出重定向**：
   - 所有输出同时显示在终端和日志文件
   - 日志文件位置：`/tmp/backend-startup.log` 和 `/tmp/frontend-startup.log`

4. **无缓冲输出**：
   - 使用 `exec` 和 `-u` 参数确保输出立即显示
   - 设置 `PYTHONUNBUFFERED=1` 确保 Python 输出不被缓冲

## 常见问题

### Q: 为什么看不到启动信息？

A: CloudStudio 的预览功能可能不会实时显示所有输出。建议：
1. 查看终端输出
2. 查看日志文件
3. 手动运行启动脚本

### Q: 如何知道服务是否启动成功？

A: 检查服务状态：
```bash
# 后端健康检查
curl http://localhost:8000/health

# 前端服务检查
curl http://localhost:5173
```

### Q: 启动脚本在哪里？

A: 启动脚本位于：
- 后端：`.vscode/start-backend-cloudstudio.sh`
- 前端：`.vscode/start-frontend-cloudstudio.sh`

### Q: 如何查看完整的启动日志？

A: 使用以下命令：
```bash
# 实时查看后端日志
tail -f /tmp/backend-startup.log

# 实时查看前端日志
tail -f /tmp/frontend-startup.log
```

## 相关文件

- `.vscode/preview.yml` - CloudStudio 预览配置
- `.vscode/start-backend-cloudstudio.sh` - 后端启动脚本
- `.vscode/start-frontend-cloudstudio.sh` - 前端启动脚本
- `/tmp/backend-startup.log` - 后端启动日志
- `/tmp/frontend-startup.log` - 前端启动日志

