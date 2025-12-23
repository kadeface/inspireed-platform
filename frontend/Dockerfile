# 前端 Dockerfile - 多阶段构建
# 阶段1: 构建阶段
FROM node:18-alpine AS builder

# 安装 pnpm
RUN npm install -g pnpm

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY package.json pnpm-lock.yaml* ./

# 安装依赖
RUN pnpm install --frozen-lockfile

# 复制源代码
COPY . .

# 构建参数（API 地址）
ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# 构建应用
RUN pnpm build

# 阶段2: 运行阶段 - 使用 Nginx 提供静态文件
FROM nginx:alpine

# 复制构建产物到 Nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置（如果存在则使用，否则使用默认配置）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]

