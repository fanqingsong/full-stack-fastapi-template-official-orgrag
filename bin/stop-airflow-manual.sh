#!/bin/bash

# Stop Airflow Manual Services Script
# Usage: ./bin/stop-airflow-manual.sh

set -e

echo "🛑 Stopping Airflow Services..."

# Stop all Airflow containers
echo ""
echo "Stopping Airflow containers..."
docker ps -a --format "{{.Names}}" | grep -E "(dev-airflow|flower)" | xargs -r docker stop 2>/dev/null || true

# Remove all Airflow containers
docker ps -a --format "{{.Names}}" | grep -E "(dev-airflow|flower)" | xargs -r docker rm 2>/dev/null || true

echo ""
echo "✅ Airflow Services Stopped!"
echo ""
echo "📝 Restart Services: ./bin/start-airflow-manual.sh"
echo ""
