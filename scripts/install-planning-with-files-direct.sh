#!/bin/bash
# install-planning-with-files-direct.sh
# 直接下载方式安装 Planning with Files skill（不依赖 Git）

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 开始安装 Planning with Files skill (直接下载方式)...${NC}"

# 配置
BASE_URL="https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/.cursor/skills/planning-with-files"
TARGET_DIR="$HOME/.cursor/skills/planning-with-files"

# 检查 curl 是否可用
if ! command -v curl &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 curl 命令${NC}"
    exit 1
fi

# 1. 创建目录结构
echo -e "${BLUE}📁 创建目录结构...${NC}"
mkdir -p "$TARGET_DIR/templates"

# 2. 下载主文件
echo -e "${BLUE}📥 下载主文件...${NC}"

download_file() {
    local url=$1
    local dest=$2
    local name=$(basename "$dest")
    
    if curl -sSL -f -o "$dest" "$url" 2>/dev/null; then
        echo -e "${GREEN}✅ ${name} 下载成功${NC}"
        return 0
    else
        echo -e "${RED}❌ ${name} 下载失败${NC}"
        return 1
    fi
}

FAILED=0

download_file "$BASE_URL/SKILL.md" "$TARGET_DIR/SKILL.md" || FAILED=1
download_file "$BASE_URL/examples.md" "$TARGET_DIR/examples.md" || echo -e "${YELLOW}⚠️  examples.md 下载失败（可选文件）${NC}"
download_file "$BASE_URL/reference.md" "$TARGET_DIR/reference.md" || echo -e "${YELLOW}⚠️  reference.md 下载失败（可选文件）${NC}"

# 3. 下载模板文件
echo -e "${BLUE}📥 下载模板文件...${NC}"
download_file "$BASE_URL/templates/task_plan.md" "$TARGET_DIR/templates/task_plan.md" || FAILED=1
download_file "$BASE_URL/templates/findings.md" "$TARGET_DIR/templates/findings.md" || FAILED=1
download_file "$BASE_URL/templates/progress.md" "$TARGET_DIR/templates/progress.md" || FAILED=1

# 4. 验证安装
echo ""
echo -e "${BLUE}🔍 验证安装...${NC}"

if [ -f "$TARGET_DIR/SKILL.md" ]; then
    echo -e "${GREEN}✅ SKILL.md 已安装${NC}"
    
    # 检查文件大小（确保不是空文件）
    if [ -s "$TARGET_DIR/SKILL.md" ]; then
        echo -e "${GREEN}✅ SKILL.md 文件大小正常${NC}"
    else
        echo -e "${RED}❌ SKILL.md 文件为空${NC}"
        FAILED=1
    fi
else
    echo -e "${RED}❌ SKILL.md 未找到${NC}"
    FAILED=1
fi

# 检查模板文件
TEMPLATE_COUNT=0
for template in task_plan.md findings.md progress.md; do
    if [ -f "$TARGET_DIR/templates/$template" ]; then
        echo -e "${GREEN}✅ $template 模板已安装${NC}"
        TEMPLATE_COUNT=$((TEMPLATE_COUNT + 1))
    else
        echo -e "${RED}❌ $template 模板未找到${NC}"
        FAILED=1
    fi
done

# 5. 显示文件结构
echo ""
echo -e "${BLUE}📂 安装的文件:${NC}"
find "$TARGET_DIR" -type f | sort

# 6. 检查 SKILL.md 的元数据
if [ -f "$TARGET_DIR/SKILL.md" ]; then
    echo ""
    echo -e "${BLUE}📋 Skill 信息:${NC}"
    head -10 "$TARGET_DIR/SKILL.md" | grep -E "name:|description:" || echo "无法读取元数据"
fi

# 7. 最终验证
if [ $FAILED -eq 0 ] && [ $TEMPLATE_COUNT -eq 3 ]; then
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
    echo -e "${YELLOW}已安装模板数量: $TEMPLATE_COUNT/3${NC}"
    exit 1
fi
