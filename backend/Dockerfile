# 后端 Dockerfile
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/storage/uploads

# 暴露端口
EXPOSE 8000

# 健康检查（使用更可靠的方法）
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# 启动命令（单进程模式，避免多进程导致的健康检查问题）
# 注意：在生产环境中，如果需要多进程，建议使用外部进程管理器（如 supervisor）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

