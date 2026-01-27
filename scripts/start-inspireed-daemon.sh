#!/bin/bash

# InspireEd 守护进程启动脚本
# 此脚本会等待 Docker 启动，然后启动所有服务

# 不使用 set -e，避免等待超时导致脚本过早退出
# set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/daemon.log"
ERROR_LOG="$LOG_DIR/daemon.error.log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$ERROR_LOG"
}

# 等待 Docker 启动（最多等待 2 分钟）
wait_for_docker() {
    log "等待 Docker 启动..."
    local max_attempts=24  # 24 * 5秒 = 120秒 = 2分钟
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker info > /dev/null 2>&1; then
            log "✅ Docker 已启动"
            # 额外等待几秒确保 Docker 完全就绪
            sleep 3
            return 0
        fi
        attempt=$((attempt + 1))
        if [ $((attempt % 5)) -eq 0 ]; then
            log "等待 Docker 启动中... ($attempt/$max_attempts)"
        fi
        sleep 5
    done
    
    log_error "Docker 在 2 分钟内未能启动，请检查 Docker Desktop 设置"
    log_error "提示：请确保 Docker Desktop 已设置为开机自动启动"
    return 1
}

# 检查服务是否已运行
is_service_running() {
    local service_name=$1
    local port=$2
    
    if [ -n "$port" ]; then
        # 通过端口检查
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            return 0
        fi
    fi
    
    # 通过进程检查
    case $service_name in
        backend)
            if pgrep -f "uvicorn app.main:app" > /dev/null; then
                return 0
            fi
            ;;
        frontend)
            if pgrep -f "pnpm dev" > /dev/null; then
                return 0
            fi
            ;;
    esac
    
    return 1
}

# 启动服务
start_services() {
    cd "$PROJECT_DIR"
    
    # 检查服务是否已运行
    local backend_running=false
    local frontend_running=false
    
    if is_service_running backend 8000; then
        backend_running=true
        log "✅ 后端服务已在运行"
    fi
    
    if is_service_running frontend 5173; then
        frontend_running=true
        log "✅ 前端服务已在运行"
    fi
    
    # 如果所有服务都在运行，跳过启动
    if [ "$backend_running" = true ] && [ "$frontend_running" = true ]; then
        log "所有服务已在运行，跳过启动"
        return 0
    fi
    
    # 启动服务（启用等待 Docker 模式）
    log "启动 InspireEd 服务..."
    export WAIT_DOCKER=true
    "$PROJECT_DIR/start.sh" >> "$LOG_FILE" 2>> "$ERROR_LOG" || {
        log_error "启动服务失败，请查看日志: $ERROR_LOG"
        return 1
    }
}

# 主函数
main() {
    log "=========================================="
    log "InspireEd 守护进程启动"
    log "=========================================="
    
    # 等待 Docker 启动（如果失败，记录错误但不退出，让 StartInterval 稍后重试）
    if ! wait_for_docker; then
        log_error "无法启动服务：Docker 未运行"
        log_error "将在 2 分钟后重试（StartInterval: 120秒）"
        # 不退出，让 LaunchAgent 稍后重试
        return 1
    fi
    
    # 启动服务
    if start_services; then
        log "✅ InspireEd 系统启动完成"
        log ""
        log "📱 访问地址："
        log "   前端应用: http://localhost:5173"
        log "   后端API: http://localhost:8000"
        log "   API文档: http://localhost:8000/docs"
        log ""
    else
        log_error "服务启动失败"
        exit 1
    fi
}

# 运行主函数
main "$@"

