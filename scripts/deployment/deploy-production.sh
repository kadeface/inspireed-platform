#!/bin/bash
# 生产环境部署脚本（增强版）
# 用于腾讯云服务器 Docker 部署

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCKER_DIR="${PROJECT_ROOT}/docker"

# 检查必要的命令
check_requirements() {
    log_step "检查系统依赖..."
    
    local missing=0
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        missing=1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装"
        missing=1
    fi
    
    if [ $missing -eq 1 ]; then
        log_error "请先安装必要的依赖"
        exit 1
    fi
    
    log_info "✓ Docker 和 Docker Compose 已安装"
}

# 检查环境配置文件
check_env_file() {
    log_step "检查环境配置文件..."
    
    local env_file="${PROJECT_ROOT}/backend/.env.prod"
    
    if [ ! -f "$env_file" ]; then
        log_error ".env.prod 文件不存在！"
        log_info "请先创建配置文件："
        log_info "  cp backend/.env.prod.example backend/.env.prod"
        log_info "  然后编辑 backend/.env.prod，设置生产环境变量"
        exit 1
    fi
    
    # 检查关键配置是否已修改
    if grep -q "CHANGE_THIS" "$env_file"; then
        log_warn "⚠️  检测到未修改的配置项（包含 CHANGE_THIS）"
        log_warn "请确保已修改所有必要的配置，特别是密码和密钥"
        read -p "是否继续部署？(y/N): " confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            exit 1
        fi
    fi
    
    log_info "✓ .env.prod 文件已存在"
}

# 数据库备份
backup_database() {
    log_step "执行数据库备份..."
    
    local backup_script="${SCRIPT_DIR}/backup-database.sh"
    
    if [ -f "$backup_script" ]; then
        if bash "$backup_script" --pre-migration; then
            log_info "✓ 数据库备份完成"
        else
            log_warn "数据库备份失败，但继续部署"
        fi
    else
        log_warn "备份脚本不存在，跳过备份"
    fi
}

# 拉取最新代码
pull_latest_code() {
    log_step "更新代码..."
    
    cd "$PROJECT_ROOT"
    
    # 检查当前分支
    local current_branch=$(git branch --show-current)
    log_info "当前分支: $current_branch"
    
    # 如果是 release 分支，拉取最新代码
    if [[ "$current_branch" == release/* ]]; then
        log_info "拉取最新代码..."
        git fetch origin "$current_branch"
        git pull origin "$current_branch"
        log_info "✓ 代码已更新"
    else
        log_warn "当前不在 release 分支，跳过代码更新"
        log_info "如需部署特定版本，请切换到对应的 release 分支"
    fi
}

# 停止旧容器
stop_old_containers() {
    log_step "停止旧容器..."
    
    cd "$DOCKER_DIR"
    
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        log_info "停止现有容器..."
        docker-compose -f docker-compose.prod.yml down
        log_info "✓ 旧容器已停止"
    else
        log_info "没有运行中的容器"
    fi
}

# 构建镜像
build_images() {
    log_step "构建 Docker 镜像..."
    
    cd "$DOCKER_DIR"
    
    log_info "这可能需要几分钟，请耐心等待..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    log_info "✓ 镜像构建完成"
}

# 启动服务
start_services() {
    log_step "启动服务..."
    
    cd "$DOCKER_DIR"
    
    docker-compose -f docker-compose.prod.yml up -d
    
    log_info "✓ 服务已启动"
}

# 等待服务健康检查
wait_for_healthy() {
    log_step "等待服务健康检查..."
    
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        local backend_status=$(docker inspect --format='{{.State.Health.Status}}' inspireed-backend 2>/dev/null || echo "starting")
        local frontend_status=$(docker inspect --format='{{.State.Health.Status}}' inspireed-frontend 2>/dev/null || echo "starting")
        local postgres_status=$(docker inspect --format='{{.State.Health.Status}}' inspireed-postgres 2>/dev/null || echo "starting")
        
        log_info "Backend: $backend_status | Frontend: $frontend_status | PostgreSQL: $postgres_status"
        
        if [ "$backend_status" = "healthy" ] && [ "$frontend_status" = "healthy" ] && [ "$postgres_status" = "healthy" ]; then
            log_info "✓ 所有服务已就绪"
            return 0
        fi
        
        sleep 5
        attempt=$((attempt + 1))
    done
    
    log_warn "服务健康检查超时"
    log_info "请手动检查容器状态："
    log_info "  docker-compose -f docker/docker-compose.prod.yml ps"
    log_info "  docker-compose -f docker/docker-compose.prod.yml logs"
}

# 运行数据库迁移
run_migrations() {
    log_step "运行数据库迁移..."
    
    # 等待后端服务就绪
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker exec inspireed-backend python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" &>/dev/null; then
            break
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    
    # 检查是否需要迁移
    local current_version=$(docker exec inspireed-backend alembic current 2>/dev/null || echo "")
    log_info "当前数据库版本: ${current_version:-未初始化}"
    
    # 执行迁移
    if docker exec inspireed-backend alembic upgrade head; then
        log_info "✓ 数据库迁移完成"
        
        # 显示迁移后版本
        local new_version=$(docker exec inspireed-backend alembic current 2>/dev/null || echo "")
        log_info "迁移后版本: $new_version"
    else
        log_error "数据库迁移失败"
        log_info "请检查日志: docker logs inspireed-backend"
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    log_info ""
    log_info "=========================================="
    log_info "✅ 部署完成！"
    log_info "=========================================="
    log_info ""
    
    # 获取服务器IP
    local server_ip=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "")
    
    log_info "📍 访问地址："
    log_info ""
    log_info "   前端: http://localhost"
    if [ -n "$server_ip" ]; then
        log_info "         http://$server_ip"
    fi
    log_info ""
    log_info "   后端 API: http://localhost:8000"
    if [ -n "$server_ip" ]; then
        log_info "            http://$server_ip:8000"
    fi
    log_info ""
    log_info "   API 文档: http://localhost:8000/docs"
    if [ -n "$server_ip" ]; then
        log_info "            http://$server_ip:8000/docs"
    fi
    log_info ""
    log_info "📝 常用命令："
    log_info ""
    log_info "   查看日志:"
    log_info "     cd docker && docker-compose -f docker-compose.prod.yml logs -f"
    log_info ""
    log_info "   查看服务状态:"
    log_info "     cd docker && docker-compose -f docker-compose.prod.yml ps"
    log_info ""
    log_info "   停止服务:"
    log_info "     cd docker && docker-compose -f docker-compose.prod.yml down"
    log_info ""
    log_info "   备份数据库:"
    log_info "     ./scripts/deployment/backup-database.sh"
    log_info ""
    log_warn "⚠️  安全提醒："
    log_warn "   1. 请立即登录并修改默认管理员密码"
    log_warn "   2. 确保 .env.prod 文件未提交到 Git"
    log_warn "   3. 定期备份数据库"
    log_info ""
    log_info "=========================================="
}

# 主流程
main() {
    log_info "=========================================="
    log_info "InspireEd 生产环境部署"
    log_info "=========================================="
    log_info ""
    
    check_requirements
    check_env_file
    
    # 询问是否备份数据库
    if docker ps --format '{{.Names}}' | grep -q "^inspireed-postgres$"; then
        read -p "是否在部署前备份数据库？(Y/n): " backup_confirm
        if [ "$backup_confirm" != "n" ] && [ "$backup_confirm" != "N" ]; then
            backup_database
        fi
    fi
    
    pull_latest_code
    stop_old_containers
    build_images
    start_services
    wait_for_healthy
    run_migrations
    
    show_deployment_info
}

# 执行主流程
main
