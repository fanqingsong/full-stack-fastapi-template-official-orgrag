#!/bin/bash

# 手动开发环境停止脚本
# 用法: ./bin/stop-dev-manual.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

echo "🛑 停止开发环境（手动模式）..."

# 检查容器是否存在并停止
echo ""
echo "停止并删除所有开发环境容器..."

# 定义所有容器名称
CONTAINERS="dev-backend dev-frontend dev-kong dev-db dev-redis dev-adminer dev-mailcatcher"

for container in $CONTAINERS; do
    if docker ps -a --format "{{.Names}}" | grep -q "^${container}$"; then
        echo "  停止: $container"
        docker stop "$container" 2>/dev/null || true
        echo "  删除: $container"
        docker rm "$container" 2>/dev/null || true
    else
        echo "  跳过 (不存在): $container"
    fi
done

echo ""
echo "✅ 开发环境已停止！"
echo ""
echo "📝 重新启动: ./bin/start-dev-manual.sh"
echo ""