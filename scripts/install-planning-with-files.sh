#!/bin/bash
# install-planning-with-files.sh
# 安装 Planning with Files skill 到 Cursor 用户 skills 目录

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 开始安装 Planning with Files skill...${NC}"

# 配置
REPO_URL="https://github.com/OthmanAdi/planning-with-files.git"
TARGET_DIR="$HOME/.cursor/skills/planning-with-files"
TEMP_DIR=$(mktemp -d)

# 清理函数
cleanup() {
    echo -e "${YELLOW}🧹 清理临时文件...${NC}"
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# 1. 检查 Git 是否可用
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 git 命令${NC}"
    echo -e "${YELLOW}请先安装 Git 或使用直接下载方式安装${NC}"
    exit 1
fi

# 2. 创建目标目录
echo -e "${BLUE}📁 创建目标目录...${NC}"
mkdir -p "$TARGET_DIR"

# 3. 克隆仓库
echo -e "${BLUE}📥 克隆仓库...${NC}"
cd "$TEMP_DIR"
if git clone "$REPO_URL" planning-with-files 2>&1; then
    echo -e "${GREEN}✅ 仓库克隆成功${NC}"
else
    echo -e "${RED}❌ 错误: 克隆仓库失败${NC}"
    exit 1
fi

# 4. 检查源目录是否存在
if [ ! -d "planning-with-files/.cursor/skills/planning-with-files" ]; then
    echo -e "${RED}❌ 错误: 找不到 skill 目录${NC}"
    echo -e "${YELLOW}尝试检查仓库结构...${NC}"
    ls -la planning-with-files/.cursor/ 2>/dev/null || echo "找不到 .cursor 目录"
    exit 1
fi

# 5. 复制文件
echo -e "${BLUE}📋 复制 skill 文件...${NC}"
cp -r planning-with-files/.cursor/skills/planning-with-files/* "$TARGET_DIR/"
echo -e "${GREEN}✅ 文件复制完成${NC}"

# 6. 验证安装
echo -e "${BLUE}🔍 验证安装...${NC}"
MISSING_FILES=0

if [ -f "$TARGET_DIR/SKILL.md" ]; then
    echo -e "${GREEN}✅ SKILL.md 已安装${NC}"
else
    echo -e "${RED}❌ SKILL.md 未找到${NC}"
    MISSING_FILES=1
fi

if [ -f "$TARGET_DIR/templates/task_plan.md" ]; then
    echo -e "${GREEN}✅ task_plan.md 模板已安装${NC}"
else
    echo -e "${YELLOW}⚠️  task_plan.md 模板未找到${NC}"
fi

if [ -f "$TARGET_DIR/templates/findings.md" ]; then
    echo -e "${GREEN}✅ findings.md 模板已安装${NC}"
else
    echo -e "${YELLOW}⚠️  findings.md 模板未找到${NC}"
fi

if [ -f "$TARGET_DIR/templates/progress.md" ]; then
    echo -e "${GREEN}✅ progress.md 模板已安装${NC}"
else
    echo -e "${YELLOW}⚠️  progress.md 模板未找到${NC}"
fi

# 7. 显示文件结构
echo ""
echo -e "${BLUE}📂 安装的文件结构:${NC}"
tree -L 3 "$TARGET_DIR" 2>/dev/null || find "$TARGET_DIR" -type f | head -10

# 8. 检查 SKILL.md 的元数据
if [ -f "$TARGET_DIR/SKILL.md" ]; then
    echo ""
    echo -e "${BLUE}📋 Skill 信息:${NC}"
    head -10 "$TARGET_DIR/SKILL.md" | grep -E "name:|description:" || echo "无法读取元数据"
fi

# 9. 最终验证
if [ $MISSING_FILES -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 安装完成！${NC}"
    echo ""
    echo -e "${BLUE}安装位置: ${NC}$TARGET_DIR"
    echo ""
    echo -e "${YELLOW}📝 下一步:${NC}"
    echo "  1. 重启 Cursor IDE 以加载新 skill"
    echo "  2. 在项目中使用 planning-with-files 功能"
    echo "  3. 查看文档: docs/PLANNING_WITH_FILES_INSTALLATION_PLAN.md"
    echo ""
else
    echo ""
    echo -e "${RED}❌ 安装不完整，请检查错误信息${NC}"
    exit 1
fi
