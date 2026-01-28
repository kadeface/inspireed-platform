#!/bin/bash
# 数据库备份脚本
# 用于生产环境数据库备份

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="${PROJECT_ROOT}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 检查 Docker 容器是否运行
check_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^inspireed-postgres$"; then
        log_error "PostgreSQL 容器未运行"
        exit 1
    fi
}

# 执行 SQL 备份
backup_sql() {
    local backup_file="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql"
    
    log_info "开始 SQL 备份..."
    
    # 执行备份
    if docker exec inspireed-postgres pg_dump -U postgres inspireed > "$backup_file"; then
        # 压缩备份文件
        gzip "$backup_file"
        local compressed_file="${backup_file}.gz"
        
        log_info "✅ SQL 备份完成: $compressed_file"
        echo "$compressed_file"
    else
        log_error "SQL 备份失败"
        exit 1
    fi
}

# 备份数据卷（完整备份）
backup_volume() {
    local backup_file="${BACKUP_DIR}/postgres_volume_${TIMESTAMP}.tar.gz"
    
    log_info "开始数据卷备份..."
    
    # 获取 volume 名称
    local volume_name=$(docker volume ls --format '{{.Name}}' | grep postgres_data | head -1)
    
    if [ -z "$volume_name" ]; then
        log_warn "未找到 postgres_data volume，跳过数据卷备份"
        return
    fi
    
    # 备份数据卷
    if docker run --rm \
        -v "$volume_name":/data:ro \
        -v "$BACKUP_DIR":/backup \
        alpine tar czf "/backup/postgres_volume_${TIMESTAMP}.tar.gz" -C /data .; then
        log_info "✅ 数据卷备份完成: $backup_file"
        echo "$backup_file"
    else
        log_error "数据卷备份失败"
        exit 1
    fi
}

# 清理旧备份（保留最近7天）
cleanup_old_backups() {
    log_info "清理7天前的备份文件..."
    
    find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +7 -delete
    find "$BACKUP_DIR" -name "postgres_volume_*.tar.gz" -mtime +7 -delete
    
    log_info "✅ 旧备份已清理"
}

# 显示备份信息
show_backup_info() {
    local sql_backup=$1
    local volume_backup=$2
    
    log_info "=========================================="
    log_info "备份完成！"
    log_info "=========================================="
    log_info "备份目录: $BACKUP_DIR"
    
    if [ -n "$sql_backup" ]; then
        local size=$(du -h "$sql_backup" | cut -f1)
        log_info "SQL 备份: $sql_backup ($size)"
    fi
    
    if [ -n "$volume_backup" ]; then
        local size=$(du -h "$volume_backup" | cut -f1)
        log_info "数据卷备份: $volume_backup ($size)"
    fi
    
    log_info ""
    log_info "恢复数据库:"
    log_info "  gunzip < $sql_backup | docker exec -i inspireed-postgres psql -U postgres inspireed"
    log_info "=========================================="
}

# 主函数
main() {
    local backup_type="all"
    local pre_migration=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --sql-only)
                backup_type="sql"
                shift
                ;;
            --volume-only)
                backup_type="volume"
                shift
                ;;
            --pre-migration)
                pre_migration=true
                shift
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    if [ "$pre_migration" = true ]; then
        log_info "⚠️  迁移前备份模式"
    fi
    
    log_info "开始数据库备份..."
    echo ""
    
    # 检查容器
    check_container
    
    # 执行备份
    local sql_backup=""
    local volume_backup=""
    
    case $backup_type in
        sql)
            sql_backup=$(backup_sql)
            ;;
        volume)
            volume_backup=$(backup_volume)
            ;;
        all)
            sql_backup=$(backup_sql)
            volume_backup=$(backup_volume)
            ;;
    esac
    
    # 清理旧备份
    cleanup_old_backups
    
    # 显示备份信息
    show_backup_info "$sql_backup" "$volume_backup"
}

# 执行主函数
main "$@"
