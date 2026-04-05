#!/bin/bash
# InspireEd 腾讯云服务器部署脚本
# 使用方法: ./deploy-to-tencent-cloud.sh [环境]
# 示例: ./deploy-to-tencent-cloud.sh prod

set -e  # 遇到错误立即退出

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

# 检查必要的命令
check_requirements() {
    log_info "检查系统依赖..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi

    log_info "✓ Docker 和 Docker Compose 已安装"
}

# 检查并创建 .env.prod
check_env_file() {
    log_info "检查环境配置文件..."

    if [ ! -f "backend/.env.prod" ]; then
        log_error ".env.prod 文件不存在！"
        log_info "请先创建 backend/.env.prod 文件，配置生产环境变量"
        log_info "可以参考 backend/.env 文件，但务必修改密码和密钥"
        exit 1
    fi

    log_info "✓ .env.prod 文件已存在"
}

# 拉取最新代码
pull_latest_code() {
    log_info "拉取最新代码..."

    git fetch origin dev
    git checkout dev
    git pull origin dev

    log_info "✓ 代码已更新到最新版本"
}

# 停止并删除旧容器
stop_old_containers() {
    log_info "停止旧容器..."

    cd docker
    docker-compose -f docker-compose.prod.yml down

    log_info "✓ 旧容器已停止"
}

# 构建新镜像
build_images() {
    log_info "构建 Docker 镜像（这可能需要几分钟）..."

    docker-compose -f docker-compose.prod.yml build --no-cache

    log_info "✓ 镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动所有服务..."

    docker-compose -f docker-compose.prod.yml up -d

    log_info "✓ 服务已启动"
}

# 等待服务健康检查
wait_for_healthy() {
    log_info "等待服务健康检查..."

    local max_attempts=60
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        local backend_status=$(docker inspect --format='{{.State.Health.Status}}' inspireed-backend 2>/dev/null || echo "starting")
        local frontend_status=$(docker inspect --format='{{.State.Health.Status}}' inspireed-frontend 2>/dev/null || echo "starting")

        log_info "Backend: $backend_status | Frontend: $frontend_status"

        if [ "$backend_status" = "healthy" ] && [ "$frontend_status" = "healthy" ]; then
            log_info "✓ 所有服务已就绪"
            return 0
        fi

        sleep 5
        attempt=$((attempt + 1))
    done

    log_warn "服务健康检查超时，请手动检查容器状态"
    docker-compose -f docker-compose.prod.yml ps
}

# 初始化数据库（首次部署）
init_database() {
    log_info "检查是否需要初始化数据库..."

    # 检查数据库是否已有数据
    local db_initialized=$(docker exec inspireed-postgres psql -U postgres -d inspireed -tAc "SELECT COUNT(*) FROM alembic_version" 2>/dev/null || echo "0")

    if [ "$db_initialized" = "0" ]; then
        log_info "数据库未初始化，开始迁移..."

        # 运行数据库迁移
        docker exec inspireed-backend alembic upgrade head

        # 创建初始管理员用户
        docker exec inspireed-backend python -c "
from app.core.security import get_password_hash
from app.models.user import User
from app.api.deps import SessionLocal
import sys

db = SessionLocal()
try:
    # 检查是否已存在管理员
    existing = db.query(User).filter(User.email == 'admin@inspireed.com').first()
    if not existing:
        admin = User(
            email='admin@inspireed.com',
            hashed_password=get_password_hash('admin123'),
            full_name='Administrator',
            is_superuser=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print('✓ 管理员用户已创建')
    else:
        print('管理员用户已存在')
except Exception as e:
    print(f'创建管理员失败: {e}', file=sys.stderr)
    sys.exit(1)
finally:
    db.close()
"

        log_info "✓ 数据库初始化完成"
    else
        log_info "数据库已初始化，跳过"
    fi
}

# 显示部署信息
show_deployment_info() {
    log_info "=========================================="
    log_info "部署完成！"
    log_info "=========================================="
    log_info "前端访问地址: http://<服务器IP>"
    log_info "后端 API: http://<服务器IP>:8000"
    log_info "API 文档: http://<服务器IP>:8000/docs"
    log_info ""
    log_info "默认管理员账号: admin@inspireed.com"
    log_info "默认密码: admin123"
    log_warn "⚠️  请立即登录并修改管理员密码！"
    log_info ""
    log_info "查看日志命令:"
    log_info "  cd docker && docker-compose -f docker-compose.prod.yml logs -f"
    log_info "=========================================="
}

# 主流程
main() {
    log_info "开始部署 InspireEd 到腾讯云..."
    echo ""

    check_requirements
    check_env_file
    pull_latest_code
    stop_old_containers
    build_images
    start_services
    wait_for_healthy
    init_database
    show_deployment_info
}

# 执行主流程
main
