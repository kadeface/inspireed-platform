# Planning with Files 快速安装指南

## 快速安装（推荐方式）

### 方式一：使用 Git 克隆（推荐）

```bash
# 运行安装脚本
./scripts/install-planning-with-files.sh
```

### 方式二：直接下载（无需 Git）

```bash
# 运行直接下载安装脚本
./scripts/install-planning-with-files-direct.sh
```

## 手动安装

### 步骤 1: 创建目录

```bash
mkdir -p ~/.cursor/skills/planning-with-files/templates
```

### 步骤 2: 下载文件

```bash
# 下载主文件
curl -o ~/.cursor/skills/planning-with-files/SKILL.md \
  https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/.cursor/skills/planning-with-files/SKILL.md

# 下载模板文件
curl -o ~/.cursor/skills/planning-with-files/templates/task_plan.md \
  https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/.cursor/skills/planning-with-files/templates/task_plan.md

curl -o ~/.cursor/skills/planning-with-files/templates/findings.md \
  https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/.cursor/skills/planning-with-files/templates/findings.md

curl -o ~/.cursor/skills/planning-with-files/templates/progress.md \
  https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/.cursor/skills/planning-with-files/templates/progress.md
```

### 步骤 3: 验证安装

```bash
# 检查文件是否存在
ls -la ~/.cursor/skills/planning-with-files/
ls -la ~/.cursor/skills/planning-with-files/templates/
```

## 安装后操作

1. **重启 Cursor IDE** - 让系统重新加载 skills
2. **测试使用** - 在项目中使用 planning-with-files 功能

## 使用示例

安装后，在项目根目录创建规划文件：

```bash
# 在项目目录中
cp ~/.cursor/skills/planning-with-files/templates/task_plan.md ./task_plan.md
cp ~/.cursor/skills/planning-with-files/templates/findings.md ./findings.md
cp ~/.cursor/skills/planning-with-files/templates/progress.md ./progress.md
```

## 故障排除

### 问题：Skill 未加载
- 重启 Cursor IDE
- 检查 `~/.cursor/skills/planning-with-files/SKILL.md` 是否存在

### 问题：权限错误
```bash
chmod 755 ~/.cursor/skills
```

## 更多信息

- 详细安装计划: [PLANNING_WITH_FILES_INSTALLATION_PLAN.md](./PLANNING_WITH_FILES_INSTALLATION_PLAN.md)
- 项目文档: https://github.com/OthmanAdi/planning-with-files
- Cursor 安装指南: https://github.com/OthmanAdi/planning-with-files/blob/master/docs/cursor.md
