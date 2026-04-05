#!/bin/bash

# 手动开发环境启动脚本（绕过 Docker Compose 问题）
# 用法: ./bin/start-dev-manual.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

ENV_FILE=".env.dev"

echo "🚀 启动开发环境（手动模式）..."
echo "📁 项目目录: $PROJECT_DIR"

# 检查环境文件是否存在
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ 错误: 环境配置文件不存在: $ENV_FILE"
    exit 1
fi

# 加载环境变量
export $(grep -v '^#' "$ENV_FILE" | grep -v '^$' | xargs)

# 清理已存在的容器
echo ""
echo "检查现有容器..."
EXISTING_CONTAINERS=$(docker ps -a --format "{{.Names}}" | grep "^dev-" || true)
if [ -n "$EXISTING_CONTAINERS" ]; then
    echo "停止并删除现有容器..."
    echo "$EXISTING_CONTAINERS" | xargs -r docker stop 2>/dev/null || true
    echo "$EXISTING_CONTAINERS" | xargs -r docker rm 2>/dev/null || true
fi

sleep 2

# 启动数据库
echo ""
echo "📦 启动数据库服务..."
docker run --name dev-db -d \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=changethis \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=app \
  postgres:18

# 启动后端
echo "⚙️  启动后端服务..."
docker run --name dev-backend -d \
  -p 8002:8000 \
  --link dev-db:db \
  -e PROJECT_NAME="Full Stack FastAPI Project" \
  -e POSTGRES_SERVER=db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=changethis \
  -e POSTGRES_DB=app \
  -e FIRST_SUPERUSER=admin@example.com \
  -e FIRST_SUPERUSER_PASSWORD=changethis \
  -e SECRET_KEY=changethis-dev-do-not-use-in-production \
  -e BACKEND_CORS_ORIGINS="http://localhost,http://localhost:5173" \
  backend-dev:latest fastapi run --reload app/main.py

# 启动前端
echo "🎨 启动前端服务..."
docker run --name dev-frontend -d \
  -p 5173:5173 \
  -v "$(pwd)/frontend:/app/frontend" \
  -e VITE_API_URL=http://localhost:8000 \
  -e NODE_ENV=development \
  frontend-dev:latest bun run dev --host 0.0.0.0

# 启动 Redis
echo "🔴 启动 Redis 服务..."
docker run --name dev-redis -d \
  -p 6379:6379 \
  redis:7-alpine redis-server --requirepass changethis

# 启动 Kong Gateway
echo "🚪 启动 Kong API Gateway..."
docker run --name dev-kong -d \
  -p 8000:8000 \
  -p 8001:8001 \
  -p 1337:1337 \
  -e KONG_PG_HOST=dev-db \
  -e KONG_PG_PASSWORD=changethis \
  kong:3.4 kong start

# 启动 Adminer（数据库管理工具）
echo "🗄️  启动 Adminer..."
docker run --name dev-adminer -d \
  -p 8080:8080 \
  --link dev-db:db \
  adminer

# 启动 Mailcatcher（邮件测试工具）
echo "📧 启动 Mailcatcher..."
docker run --name dev-mailcatcher -d \
  -p 1080:1080 \
  -p 1025:1025 \
  schickling/mailcatcher

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📋 服务状态:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "dev-"

echo ""
echo "✅ 开发环境启动完成！"
echo ""
echo "🌐 访问地址:"
echo "  📌 主要应用:"
echo "    - Frontend: http://localhost:5173"
echo "    - Backend API (直接): http://localhost:8002"
echo "    - Backend API (通过 Kong): http://localhost:8000"
echo ""
echo "  📌 管理工具:"
echo "    - Adminer (数据库): http://localhost:8080"
echo "      服务器: dev-db"
echo "      用户: postgres"
echo "      密码: changethis"
echo "      数据库: app"
echo "    - Mailcatcher (邮件): http://localhost:1080"
echo "      SMTP: localhost:1025"
echo ""
echo "  📌 API 网关:"
echo "    - Kong API Gateway: http://localhost:8000"
echo "    - Kong Admin API: http://localhost:8001"
echo ""
echo "🔐 默认用户:"
echo "    - 超级用户: admin@example.com / changethis"
echo ""
echo "🧪 测试服务:"
echo "    curl http://localhost:8002/api/v1/utils/health-check/"
echo ""
echo "📝 查看日志:"
echo "    docker logs dev-backend --tail 50 -f"
echo "    docker logs dev-frontend --tail 50 -f"
echo ""
echo "🛑 停止服务: ./bin/stop-dev-manual.sh"
echo ""