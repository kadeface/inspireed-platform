# Planning with Files 安装计划

## 项目概述

**Planning with Files** 是一个基于 Manus 工作流的 Cursor Skill，通过持久化的 Markdown 文件进行任务规划、进度跟踪和知识存储。

- **GitHub 仓库**: https://github.com/OthmanAdi/planning-with-files
- **安装位置**: `~/.cursor/skills/planning-with-files/`
- **Skill 名称**: `planning-with-files`
- **版本**: 2.7.1

## 项目结构分析

### 源项目结构
```
planning-with-files/
├── .cursor/
│   └── skills/
│       └── planning-with-files/
│           ├── SKILL.md              # 主技能文件（必需）
│           ├── examples.md           # 使用示例
│           ├── reference.md          # 参考文档
│           └── templates/            # 模板文件
│               ├── task_plan.md      # 任务计划模板
│               ├── findings.md       # 研究发现模板
│               └── progress.md       # 进度跟踪模板
├── docs/
│   └── cursor.md                    # Cursor 安装指南
└── README.md
```

### 目标安装结构
```
~/.cursor/
└── skills/
    └── planning-with-files/
        ├── SKILL.md
        ├── examples.md
        ├── reference.md
        └── templates/
            ├── task_plan.md
            ├── findings.md
            └── progress.md
```

## 安装方案

### 方案一：Git 克隆 + 复制（推荐）

**优点**：
- 可以随时更新
- 保留 Git 历史
- 易于维护

**步骤**：
1. 克隆仓库到临时目录
2. 复制 `.cursor/skills/planning-with-files/` 到 `~/.cursor/skills/`
3. 清理临时文件

### 方案二：直接下载文件

**优点**：
- 不依赖 Git
- 快速安装
- 文件更少

**步骤**：
1. 创建目标目录
2. 逐个下载文件
3. 验证文件完整性

## 详细安装步骤

### 阶段一：准备工作

1. **检查 Cursor 目录结构**
   ```bash
   # 检查 ~/.cursor 目录是否存在
   ls -la ~/.cursor
   
   # 创建 skills 目录（如果不存在）
   mkdir -p ~/.cursor/skills
   ```

2. **确认安装位置**
   ```bash
   # 目标路径
   TARGET_DIR="$HOME/.cursor/skills/planning-with-files"
   echo "安装目标: $TARGET_DIR"
   ```

### 阶段二：下载和安装

#### 使用方案一（Git 克隆）

```bash
# 1. 创建临时目录
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# 2. 克隆仓库
git clone https://github.com/OthmanAdi/planning-with-files.git

# 3. 创建目标目录
mkdir -p ~/.cursor/skills/planning-with-files

# 4. 复制 skill 文件
cp -r planning-with-files/.cursor/skills/planning-with-files/* ~/.cursor/skills/planning-with-files/

# 5. 清理临时文件
cd ~
rm -rf "$TEMP_DIR"
```

#### 使用方案二（直接下载）

```bash
# 1. 创建目标目录
mkdir -p ~/.cursor/skills/planning-with-files/templates

# 2. 下载主文件
curl -o ~/.cursor/skills/planning-with-files/SKILL.md \
  https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/.cursor/skills/planning-with-files/SKILL.md

curl -o ~/.cursor/skills/planning-with-files/examples.md \
  https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/.cursor/skills/planning-with-files/examples.md

curl -o ~/.cursor/skills/planning-with-files/reference.md \
  https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/.cursor/skills/planning-with-files/reference.md

# 3. 下载模板文件
curl -o ~/.cursor/skills/planning-with-files/templates/task_plan.md \
  https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/.cursor/skills/planning-with-files/templates/task_plan.md

curl -o ~/.cursor/skills/planning-with-files/templates/findings.md \
  https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/.cursor/skills/planning-with-files/templates/findings.md

curl -o ~/.cursor/skills/planning-with-files/templates/progress.md \
  https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/.cursor/skills/planning-with-files/templates/progress.md
```

### 阶段三：验证安装

1. **检查文件结构**
   ```bash
   tree ~/.cursor/skills/planning-with-files
   # 或
   ls -laR ~/.cursor/skills/planning-with-files
   ```

2. **验证必需文件**
   ```bash
   # 检查 SKILL.md 是否存在
   test -f ~/.cursor/skills/planning-with-files/SKILL.md && echo "✅ SKILL.md 存在" || echo "❌ SKILL.md 缺失"
   
   # 检查模板文件
   test -f ~/.cursor/skills/planning-with-files/templates/task_plan.md && echo "✅ task_plan.md 存在" || echo "❌ task_plan.md 缺失"
   ```

3. **验证文件内容**
   ```bash
   # 检查 SKILL.md 的 frontmatter
   head -20 ~/.cursor/skills/planning-with-files/SKILL.md | grep -E "name:|description:"
   ```

### 阶段四：测试使用

1. **重启 Cursor IDE**（让系统重新加载 skills）

2. **测试 skill 是否可用**
   - 在 Cursor 中打开一个新项目
   - 尝试使用 planning-with-files 相关的功能
   - 检查 skill 是否出现在可用技能列表中

## 安装脚本

### 自动化安装脚本（方案一）

```bash
#!/bin/bash
# install-planning-with-files.sh

set -e

echo "🚀 开始安装 Planning with Files skill..."

# 配置
REPO_URL="https://github.com/OthmanAdi/planning-with-files.git"
TARGET_DIR="$HOME/.cursor/skills/planning-with-files"
TEMP_DIR=$(mktemp -d)

# 清理函数
cleanup() {
    echo "🧹 清理临时文件..."
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# 1. 创建目标目录
echo "📁 创建目标目录..."
mkdir -p "$TARGET_DIR"

# 2. 克隆仓库
echo "📥 克隆仓库..."
cd "$TEMP_DIR"
git clone "$REPO_URL" planning-with-files

# 3. 复制文件
echo "📋 复制 skill 文件..."
if [ -d "planning-with-files/.cursor/skills/planning-with-files" ]; then
    cp -r planning-with-files/.cursor/skills/planning-with-files/* "$TARGET_DIR/"
    echo "✅ 文件复制完成"
else
    echo "❌ 错误: 找不到 skill 目录"
    exit 1
fi

# 4. 验证安装
echo "🔍 验证安装..."
if [ -f "$TARGET_DIR/SKILL.md" ]; then
    echo "✅ SKILL.md 已安装"
else
    echo "❌ 错误: SKILL.md 未找到"
    exit 1
fi

# 5. 显示安装信息
echo ""
echo "✅ 安装完成！"
echo ""
echo "安装位置: $TARGET_DIR"
echo ""
echo "📝 下一步:"
echo "  1. 重启 Cursor IDE 以加载新 skill"
echo "  2. 在项目中使用 planning-with-files 功能"
echo ""
```

### 自动化安装脚本（方案二 - 直接下载）

```bash
#!/bin/bash
# install-planning-with-files-direct.sh

set -e

echo "🚀 开始安装 Planning with Files skill (直接下载方式)..."

# 配置
BASE_URL="https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/.cursor/skills/planning-with-files"
TARGET_DIR="$HOME/.cursor/skills/planning-with-files"

# 1. 创建目录结构
echo "📁 创建目录结构..."
mkdir -p "$TARGET_DIR/templates"

# 2. 下载主文件
echo "📥 下载主文件..."
curl -sSL -o "$TARGET_DIR/SKILL.md" "$BASE_URL/SKILL.md"
curl -sSL -o "$TARGET_DIR/examples.md" "$BASE_URL/examples.md"
curl -sSL -o "$TARGET_DIR/reference.md" "$BASE_URL/reference.md"

# 3. 下载模板文件
echo "📥 下载模板文件..."
curl -sSL -o "$TARGET_DIR/templates/task_plan.md" "$BASE_URL/templates/task_plan.md"
curl -sSL -o "$TARGET_DIR/templates/findings.md" "$BASE_URL/templates/findings.md"
curl -sSL -o "$TARGET_DIR/templates/progress.md" "$BASE_URL/templates/progress.md"

# 4. 验证安装
echo "🔍 验证安装..."
if [ -f "$TARGET_DIR/SKILL.md" ]; then
    echo "✅ SKILL.md 已安装"
    echo "✅ 模板文件已安装"
    echo ""
    echo "✅ 安装完成！"
    echo ""
    echo "安装位置: $TARGET_DIR"
    echo ""
    echo "📝 下一步:"
    echo "  1. 重启 Cursor IDE 以加载新 skill"
    echo "  2. 在项目中使用 planning-with-files 功能"
else
    echo "❌ 错误: 安装失败"
    exit 1
fi
```

## 故障排除

### 问题 1: 目录不存在
**错误**: `mkdir: cannot create directory`
**解决**: 手动创建父目录
```bash
mkdir -p ~/.cursor/skills
```

### 问题 2: 权限问题
**错误**: `Permission denied`
**解决**: 检查目录权限
```bash
chmod 755 ~/.cursor/skills
```

### 问题 3: Skill 未加载
**解决**: 
1. 重启 Cursor IDE
2. 检查 SKILL.md 格式是否正确
3. 查看 Cursor 日志

### 问题 4: 网络问题
**解决**: 使用代理或镜像
```bash
# 设置代理（如果需要）
export https_proxy=http://proxy.example.com:8080
```

## 更新计划

### 如何更新已安装的 skill

```bash
# 方案一：重新运行安装脚本
./install-planning-with-files.sh

# 方案二：手动更新
cd ~/.cursor/skills/planning-with-files
git pull  # 如果使用 git 方式安装
```

## 卸载计划

```bash
# 删除 skill 目录
rm -rf ~/.cursor/skills/planning-with-files

# 验证删除
test -d ~/.cursor/skills/planning-with-files && echo "❌ 删除失败" || echo "✅ 已删除"
```

## 使用说明

安装完成后，在 Cursor 中使用：

1. **创建规划文件**：在项目根目录创建 `task_plan.md`, `findings.md`, `progress.md`
2. **使用模板**：参考 `~/.cursor/skills/planning-with-files/templates/` 中的模板
3. **遵循工作流**：按照 SKILL.md 中的说明使用文件规划模式

## 参考文档

- [Cursor 安装指南](https://github.com/OthmanAdi/planning-with-files/blob/master/docs/cursor.md)
- [项目 README](https://github.com/OthmanAdi/planning-with-files)
- [快速开始指南](https://github.com/OthmanAdi/planning-with-files/blob/master/docs/quickstart.md)

## 检查清单

安装前：
- [ ] 确认 Cursor IDE 已安装
- [ ] 确认有网络连接
- [ ] 确认有足够的磁盘空间

安装中：
- [ ] 创建目标目录
- [ ] 下载/复制所有必需文件
- [ ] 验证文件完整性

安装后：
- [ ] 验证文件结构正确
- [ ] 重启 Cursor IDE
- [ ] 测试 skill 是否可用
- [ ] 阅读使用文档

---

**创建日期**: 2026-01-24
**最后更新**: 2026-01-24
