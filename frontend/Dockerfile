# 前端 Dockerfile - 多阶段构建
# 阶段1: 构建阶段
FROM node:18-alpine AS builder

# 安装 pnpm
RUN npm install -g pnpm

# 设置工作目录
WORKDIR /app

# 复制 pnpm workspace 配置和 lockfile
COPY pnpm-workspace.yaml pnpm-lock.yaml package.json ./

# 创建 shared 目录和最小 package.json（pnpm workspace 要求所有列出的包都存在）
RUN mkdir -p shared && echo '{"name":"shared","version":"1.0.0","private":true}' > shared/package.json

# 复制 frontend package.json
COPY frontend/package.json ./frontend/

# 安装依赖（使用 workspace）
RUN pnpm install --frozen-lockfile

# 复制 frontend 源代码
COPY frontend/ ./frontend/

# 构建参数（API 地址）
ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# 构建应用（使用 workspace filter，从根目录执行）
WORKDIR /app
RUN pnpm --filter frontend build

# 阶段2: 运行阶段 - 使用 Nginx 提供静态文件
FROM nginx:alpine

# 复制构建产物到 Nginx 目录
COPY --from=builder /app/frontend/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]

