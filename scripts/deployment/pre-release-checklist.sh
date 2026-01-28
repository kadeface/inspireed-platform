#!/bin/bash
# 发布前检查清单脚本
# 用于验证代码质量和部署准备

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查结果
PASSED=0
FAILED=0
WARNINGS=0

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    FAILED=$((FAILED + 1))
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASSED=$((PASSED + 1))
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 检查 Git 状态
check_git_status() {
    log_step "检查 Git 状态..."
    
    cd "$PROJECT_ROOT"
    
    # 检查是否在 release 分支
    local current_branch=$(git branch --show-current)
    if [[ "$current_branch" != release/* ]]; then
        log_warn "当前不在 release 分支: $current_branch"
        log_info "建议从 dev 分支创建 release 分支"
    else
        log_pass "当前在 release 分支: $current_branch"
    fi
    
    # 检查工作区是否干净
    if [ -n "$(git status --porcelain)" ]; then
        log_error "工作区有未提交的更改"
        git status --short
    else
        log_pass "工作区干净"
    fi
    
    # 检查是否有未推送的提交
    local ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
    if [ "$ahead" -gt 0 ]; then
        log_warn "有 $ahead 个未推送的提交"
    else
        log_pass "所有提交已推送"
    fi
}

# 检查环境变量文件
check_env_files() {
    log_step "检查环境变量文件..."
    
    # 检查 .env.prod 是否存在
    if [ -f "${PROJECT_ROOT}/backend/.env.prod" ]; then
        log_pass ".env.prod 文件存在"
        
        # 检查是否包含敏感信息（不应该提交到 Git）
        if git ls-files --error-unmatch backend/.env.prod &>/dev/null; then
            log_error ".env.prod 文件被 Git 跟踪！这很危险！"
            log_info "请从 Git 中移除: git rm --cached backend/.env.prod"
        else
            log_pass ".env.prod 未提交到 Git"
        fi
        
        # 检查是否包含默认值
        if grep -q "CHANGE_THIS" "${PROJECT_ROOT}/backend/.env.prod"; then
            log_warn ".env.prod 包含未修改的配置项"
        else
            log_pass ".env.prod 配置已更新"
        fi
    else
        log_warn ".env.prod 文件不存在（部署时需要）"
    fi
    
    # 检查 .gitignore
    if grep -q "\.env\.prod" "${PROJECT_ROOT}/.gitignore" 2>/dev/null || \
       grep -q "\.env\.prod" "${PROJECT_ROOT}/backend/.gitignore" 2>/dev/null; then
        log_pass ".env.prod 已在 .gitignore 中"
    else
        log_warn ".env.prod 未在 .gitignore 中"
    fi
}

# 检查数据库迁移
check_migrations() {
    log_step "检查数据库迁移..."
    
    local migrations_dir="${PROJECT_ROOT}/backend/alembic/versions"
    
    if [ ! -d "$migrations_dir" ]; then
        log_error "迁移目录不存在: $migrations_dir"
        return
    fi
    
    # 检查迁移文件
    local migration_count=$(find "$migrations_dir" -name "*.py" -type f | wc -l)
    if [ "$migration_count" -eq 0 ]; then
        log_warn "没有找到迁移文件"
    else
        log_pass "找到 $migration_count 个迁移文件"
    fi
    
    # 检查迁移文件命名
    local invalid_names=$(find "$migrations_dir" -name "*.py" -type f ! -name "[0-9a-f]*_*.py" | wc -l)
    if [ "$invalid_names" -gt 0 ]; then
        log_warn "有 $invalid_names 个迁移文件命名不规范"
    else
        log_pass "迁移文件命名规范"
    fi
}

# 检查代码质量（如果可用）
check_code_quality() {
    log_step "检查代码质量..."
    
    # 检查 Python 代码（如果安装了 black）
    if command -v black &> /dev/null; then
        cd "${PROJECT_ROOT}/backend"
        if black --check . &>/dev/null; then
            log_pass "Python 代码格式检查通过"
        else
            log_warn "Python 代码格式需要调整（运行 black .）"
        fi
    else
        log_info "black 未安装，跳过代码格式检查"
    fi
    
    # 检查 TypeScript/Vue 代码（如果安装了相关工具）
    if [ -f "${PROJECT_ROOT}/frontend/package.json" ]; then
        cd "${PROJECT_ROOT}/frontend"
        if [ -f "node_modules/.bin/eslint" ] || command -v eslint &> /dev/null; then
            log_info "可以运行 ESLint 检查（可选）"
        fi
    fi
}

# 检查 Docker 配置
check_docker_config() {
    log_step "检查 Docker 配置..."
    
    local docker_compose="${PROJECT_ROOT}/docker/docker-compose.prod.yml"
    
    if [ ! -f "$docker_compose" ]; then
        log_error "docker-compose.prod.yml 不存在"
        return
    fi
    
    log_pass "docker-compose.prod.yml 存在"
    
    # 检查数据库端口是否仅绑定到本地
    if grep -q "127.0.0.1:5432:5432" "$docker_compose"; then
        log_pass "数据库端口仅绑定到本地"
    else
        log_warn "数据库端口配置需要检查"
    fi
    
    # 检查是否有健康检查
    if grep -q "healthcheck:" "$docker_compose"; then
        log_pass "Docker 服务配置了健康检查"
    else
        log_warn "部分服务可能缺少健康检查"
    fi
}

# 检查依赖版本
check_dependencies() {
    log_step "检查依赖版本..."
    
    # 检查 Python 依赖
    if [ -f "${PROJECT_ROOT}/backend/requirements.txt" ]; then
        log_pass "requirements.txt 存在"
        
        # 检查是否有固定版本
        local pinned=$(grep -c "==" "${PROJECT_ROOT}/backend/requirements.txt" || echo "0")
        if [ "$pinned" -gt 0 ]; then
            log_pass "Python 依赖已固定版本 ($pinned 个)"
        else
            log_warn "Python 依赖未固定版本"
        fi
    fi
    
    # 检查 Node.js 依赖
    if [ -f "${PROJECT_ROOT}/frontend/package.json" ]; then
        log_pass "package.json 存在"
        
        if [ -f "${PROJECT_ROOT}/frontend/pnpm-lock.yaml" ] || \
           [ -f "${PROJECT_ROOT}/frontend/package-lock.json" ]; then
            log_pass "前端依赖锁定文件存在"
        else
            log_warn "前端依赖锁定文件不存在"
        fi
    fi
}

# 检查安全配置
check_security() {
    log_step "检查安全配置..."
    
    # 检查是否有硬编码的密码
    local hardcoded_passwords=$(grep -r "password.*=.*['\"].*[^=]" \
        "${PROJECT_ROOT}/backend/app" \
        --include="*.py" 2>/dev/null | grep -v "get_password_hash\|hashed_password" | wc -l || echo "0")
    
    if [ "$hardcoded_passwords" -gt 0 ]; then
        log_warn "可能发现硬编码的密码（需要人工检查）"
    else
        log_pass "未发现明显的硬编码密码"
    fi
    
    # 检查 SECRET_KEY
    if grep -r "SECRET_KEY.*=.*['\"].*change.*" \
        "${PROJECT_ROOT}/backend" \
        --include="*.py" &>/dev/null; then
        log_warn "可能使用了默认的 SECRET_KEY"
    else
        log_pass "SECRET_KEY 配置检查通过"
    fi
}

# 显示检查结果
show_results() {
    log_info ""
    log_info "=========================================="
    log_info "检查完成"
    log_info "=========================================="
    log_info ""
    log_info "通过: $PASSED"
    log_warn "警告: $WARNINGS"
    log_error "失败: $FAILED"
    log_info ""
    
    if [ $FAILED -eq 0 ]; then
        if [ $WARNINGS -eq 0 ]; then
            log_info "✅ 所有检查通过，可以发布！"
            return 0
        else
            log_warn "⚠️  有警告项，建议修复后再发布"
            return 1
        fi
    else
        log_error "❌ 有失败项，请修复后再发布"
        return 1
    fi
}

# 主函数
main() {
    log_info "=========================================="
    log_info "发布前检查清单"
    log_info "=========================================="
    log_info ""
    
    check_git_status
    check_env_files
    check_migrations
    check_code_quality
    check_docker_config
    check_dependencies
    check_security
    
    show_results
}

# 执行主函数
main
