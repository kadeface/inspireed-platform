# 后端 Dockerfile
# 若拉取 docker.io 超时，可用镜像：docker build --build-arg BASE_IMAGE=docker.m.daocloud.io/library/python:3.10-slim .
# 或在 Docker Desktop 配置 registry-mirrors（如 https://docker.mirrors.ustc.edu.cn）
ARG BASE_IMAGE=python:3.10-slim
FROM ${BASE_IMAGE}

# 设置工作目录
WORKDIR /app

# 配置使用国内镜像源（阿里云）以加速 apt-get
# 如果是 CloudStudio 环境，使用国内镜像源可以大幅提升构建速度
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || \
    (echo "deb http://mirrors.aliyun.com/debian/ bullseye main" > /etc/apt/sources.list && \
     echo "deb http://mirrors.aliyun.com/debian-security/ bullseye-security main" >> /etc/apt/sources.list && \
     echo "deb http://mirrors.aliyun.com/debian/ bullseye-updates main" >> /etc/apt/sources.list) || true

# 安装系统依赖（添加超时和重试机制）
RUN apt-get update --fix-missing && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# pip 源：默认清华大学镜像（国内加速）；需官方源可：--build-arg PIP_INDEX_URL=https://pypi.org/simple
# 慢速网络可加大超时：--build-arg PIP_TIMEOUT=600
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/
ARG PIP_TIMEOUT=300
RUN pip install --no-cache-dir --index-url "$PIP_INDEX_URL" --timeout "$PIP_TIMEOUT" --retries 5 -r requirements.txt

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

