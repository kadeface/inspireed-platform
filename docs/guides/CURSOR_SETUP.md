# Cursor IDE 集成设置指南

本指南将帮助您在 macOS 上设置 Cursor IDE 的命令行集成，以便在终端中直接使用 `cursor` 命令。

## 📋 方法一：通过命令面板安装（推荐）

### 步骤 1：打开命令面板

1. **在 Cursor IDE 中**，按下快捷键：
   ```
   Cmd + Shift + P
   ```
   或者
   - 点击顶部菜单栏：**View** → **Command Palette...**

### 步骤 2：搜索并运行安装命令

1. 在命令面板的搜索框中输入：
   ```
   Shell Command: Install 'cursor' command in PATH
   ```

2. 从搜索结果中选择：
   ```
   Shell Command: Install 'cursor' command in PATH
   ```

3. 点击回车或点击该选项

### 步骤 3：确认安装

- 如果安装成功，您会看到提示信息（通常在右下角或顶部通知区域）
- 如果已经安装过，可能会提示已存在

### 步骤 4：验证安装

1. **打开终端**（Terminal.app 或 iTerm2）

2. **运行以下命令验证**：
   ```bash
   cursor --version
   ```

3. **如果显示版本号**，说明安装成功！例如：
   ```
   cursor 0.40.0
   ```

## 📋 方法二：手动安装（如果方法一失败）

如果通过命令面板安装失败，可以手动创建符号链接：

### 步骤 1：找到 Cursor 应用路径

Cursor 通常安装在：
```
/Applications/Cursor.app
```

### 步骤 2：创建符号链接

在终端中运行：

```bash
# 创建符号链接到 /usr/local/bin（需要管理员权限）
sudo ln -s /Applications/Cursor.app/Contents/Resources/app/bin/cursor /usr/local/bin/cursor
```

或者，如果您使用 Homebrew 安装的 Cursor：

```bash
# 检查 Cursor 的实际路径
which cursor
```

### 步骤 3：添加到 PATH（如果需要）

如果 `/usr/local/bin` 不在您的 PATH 中，需要添加到 shell 配置文件：

**对于 zsh（macOS 默认）：**
```bash
# 编辑 ~/.zshrc
nano ~/.zshrc

# 添加以下行
export PATH="/usr/local/bin:$PATH"

# 保存并退出（Ctrl+O, Enter, Ctrl+X）

# 重新加载配置
source ~/.zshrc
```

**对于 bash：**
```bash
# 编辑 ~/.bash_profile
nano ~/.bash_profile

# 添加以下行
export PATH="/usr/local/bin:$PATH"

# 保存并退出（Ctrl+O, Enter, Ctrl+X）

# 重新加载配置
source ~/.bash_profile
```

## 🧪 测试和使用

安装成功后，您可以在终端中使用以下命令：

### 1. 打开文件或目录

```bash
# 打开当前目录
cursor .

# 打开特定文件
cursor README.md

# 打开特定目录
cursor /path/to/directory
```

### 2. 在特定行打开文件

```bash
# 打开文件并跳转到第 100 行
cursor --goto README.md:100
```

### 3. 比较文件

```bash
# 比较两个文件
cursor --diff file1.txt file2.txt
```

### 4. 检查版本

```bash
cursor --version
```

## ❓ 常见问题

### Q1: 命令未找到（command not found）

**解决方案：**
1. 确认 Cursor 应用已正确安装
2. 检查 PATH 环境变量：
   ```bash
   echo $PATH
   ```
3. 确认符号链接存在：
   ```bash
   ls -la /usr/local/bin/cursor
   ```

### Q2: 权限被拒绝（Permission denied）

**解决方案：**
```bash
# 给符号链接添加执行权限
chmod +x /usr/local/bin/cursor
```

### Q3: 命令面板中找不到安装选项

**可能原因：**
- Cursor 版本较旧，不支持此功能
- 需要更新 Cursor 到最新版本

**解决方案：**
1. 检查 Cursor 版本：**Cursor** → **About Cursor**
2. 更新到最新版本：**Cursor** → **Check for Updates**
3. 或使用手动安装方法（方法二）

### Q4: 安装后仍然无法使用

**解决方案：**
1. **重启终端**：关闭并重新打开终端窗口
2. **检查 shell 类型**：
   ```bash
   echo $SHELL
   ```
3. **重新加载 shell 配置**：
   ```bash
   # zsh
   source ~/.zshrc
   
   # bash
   source ~/.bash_profile
   ```

## 📝 验证清单

完成安装后，请确认：

- [ ] 命令面板中成功运行了安装命令
- [ ] 终端中可以运行 `cursor --version`
- [ ] 可以使用 `cursor .` 打开当前目录
- [ ] 可以使用 `cursor filename` 打开文件

## 🔗 相关资源

- [Cursor 官方文档](https://cursor.sh/docs)
- [Cursor GitHub](https://github.com/getcursor/cursor)

## 💡 提示

- 安装后，您可以在任何终端窗口中使用 `cursor` 命令
- 这对于快速打开项目、文件或目录非常有用
- 也可以集成到其他脚本和工具中

---

**最后更新：** 2025-01-27
