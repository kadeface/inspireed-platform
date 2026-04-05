#!/bin/bash

# InspireEd HTTPS 配置脚本
# 用于配置 SSL 证书（支持 Let's Encrypt 免费证书）

set -e

echo "=========================================="
echo "InspireEd HTTPS 配置向导"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用 sudo 运行此脚本${NC}"
    echo "使用方法: sudo ./setup-https.sh"
    exit 1
fi

# 检查是否安装了 docker 和 docker-compose
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 未安装 Docker${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: 未安装 docker-compose${NC}"
    exit 1
fi

echo ""
echo "请选择证书配置方式:"
echo "1) 使用 Let's Encrypt 免费证书 (推荐，需要域名)"
echo "2) 使用自签名证书 (测试用，浏览器仍会提示但不影响功能)"
echo "3) 使用已有证书文件"
echo ""
read -p "请输入选项 [1-3]: " cert_option

case $cert_option in
    1)
        # Let's Encrypt 证书配置
        echo ""
        echo -e "${GREEN}配置 Let's Encrypt 免费证书${NC}"
        echo ""
        read -p "请输入你的域名 (例如: inspireed.example.com): " domain_name

        if [ -z "$domain_name" ]; then
            echo -e "${RED}错误: 域名不能为空${NC}"
            exit 1
        fi

        echo ""
        echo "将使用域名: $domain_name"
        echo ""

        # 安装 certbot
        if ! command -v certbot &> /dev/null; then
            echo "安装 Certbot..."
            apt-get update
            apt-get install -y certbot
        fi

        # 创建证书目录
        mkdir -p ./docker/ssl/certbot

        # 获取证书（使用 standalone 模式，需要先停止 nginx）
        echo "正在获取 Let's Encrypt 证书..."
        echo "注意: 此时会临时启动 Certbot 的 Web 服务器，需要确保 80 端口可用"

        # 停止可能占用 80 端口的服务
        docker-compose -f docker/docker-compose.prod.yml down frontend 2>/dev/null || true

        certbot certonly --standalone \
            -d "$domain_name" \
            --email "admin@$domain_name" \
            --agree-tos \
            --non-interactive \
            --keep-until-expiring

        # 复制证书到项目目录
        mkdir -p ./docker/ssl/live
        cp "/etc/letsencrypt/live/$domain_name/fullchain.pem" ./docker/ssl/
        cp "/etc/letsencrypt/live/$domain_name/privkey.pem" ./docker/ssl/

        echo -e "${GREEN}证书获取成功！${NC}"
        echo "证书位置: ./docker/ssl/"
        echo ""
        echo "⚠️  重要: Let's Encrypt 证书有效期为 90 天"
        echo "建议设置自动续期任务（cron）:"
        echo "  0 0 * * 0 certbot renew --quiet && docker restart inspireed-frontend"
        ;;

    2)
        # 自签名证书
        echo ""
        echo -e "${YELLOW}生成自签名证书（测试用）${NC}"
        echo ""

        # 创建证书目录
        mkdir -p ./docker/ssl

        # 生成自签名证书（有效期 1 年）
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ./docker/ssl/privkey.pem \
            -out ./docker/ssl/fullchain.pem \
            -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"

        echo -e "${GREEN}自签名证书生成成功！${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  注意: 使用自签名证书时，浏览器会显示安全警告${NC}"
        echo "这是正常的，可以点击「继续访问」或「高级」->「继续」"
        ;;

    3)
        # 使用已有证书
        echo ""
        echo "使用已有证书文件"
        echo ""

        read -p "请输入证书文件路径 (fullchain.pem): " cert_path
        read -p "请输入私钥文件路径 (privkey.pem): " key_path

        if [ ! -f "$cert_path" ] || [ ! -f "$key_path" ]; then
            echo -e "${RED}错误: 文件不存在${NC}"
            exit 1
        fi

        # 创建证书目录
        mkdir -p ./docker/ssl

        # 复制证书
        cp "$cert_path" ./docker/ssl/fullchain.pem
        cp "$key_path" ./docker/ssl/privkey.pem

        echo -e "${GREEN}证书文件复制成功！${NC}"
        ;;

    *)
        echo -e "${RED}无效的选项${NC}"
        exit 1
        ;;
esac

# 设置证书文件权限
chmod 644 ./docker/ssl/fullchain.pem
chmod 600 ./docker/ssl/privkey.pem

echo ""
echo "=========================================="
echo -e "${GREEN}SSL 证书配置完成！${NC}"
echo "=========================================="
echo ""
echo "下一步操作:"
echo "1. 更新 docker-compose.prod.yml 中的端口映射:"
echo "   - 80:80   (HTTP, 用于重定向)"
echo "   - 443:443 (HTTPS)"
echo ""
echo "2. 更新 frontend 的配置使用 nginx-https.conf:"
echo "   将 nginx.conf 改为 nginx-https.conf"
echo ""
echo "3. 重启服务:"
echo "   docker-compose -f docker/docker-compose.prod.yml up -d"
echo ""
echo "4. 访问测试:"
echo "   https://your-domain.com"
echo ""
