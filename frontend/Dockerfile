# 前端 Dockerfile - 多阶段构建
# 阶段1: 构建阶段
FROM node:20-alpine AS builder

# 安装 pnpm
RUN npm install -g pnpm

# 设置工作目录
WORKDIR /app

# 复制 package.json
COPY package.json ./

# 安装依赖（不使用 workspace 模式，直接在当前目录安装）
# 注意：这里不使用 --frozen-lockfile，因为可能没有 lockfile
RUN pnpm install

# 复制源代码
COPY . ./

# 构建参数：留空则运行时走同源 /api/v1（Nginx 反代 backend，仅对外开放 80）
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# 构建应用
RUN pnpm build

# 阶段2: 运行阶段 - 使用 Nginx 提供静态文件
FROM nginx:alpine

# 复制构建产物到 Nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx：map 须在 http 上下文（conf.d 内先于 server）
COPY nginx-map.conf /etc/nginx/conf.d/00-map.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]

