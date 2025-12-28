# 前端 Dockerfile - 多阶段构建
# 阶段1: 构建阶段
FROM node:18-alpine AS builder

# 安装 pnpm
RUN npm install -g pnpm

# 设置工作目录为 frontend
WORKDIR /app

# 复制 frontend package.json
COPY frontend/package.json ./

# 安装依赖（不使用 workspace 模式，直接在 frontend 目录安装）
# 注意：这里不使用 --frozen-lockfile，因为 lockfile 在根目录
RUN pnpm install

# 复制 frontend 源代码
COPY frontend/ ./

# 构建参数（API 地址）
ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# 构建应用
RUN pnpm build

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

