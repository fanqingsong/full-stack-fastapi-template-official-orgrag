#!/bin/bash

# Airflow Manual Startup Script
# This script starts Airflow services manually, bypassing Docker Compose issues

set -e

echo "🚀 Starting Airflow Services (Manual Mode)..."
echo "📁 Project Directory: $(pwd)"

# Clean existing Airflow containers
echo ""
echo "Cleaning existing Airflow containers..."
docker ps -a --format "{{.Names}}" | grep -E "(airflow|flower)" | xargs -r docker stop 2>/dev/null || true
docker ps -a --format "{{.Names}}" | grep -E "(airflow|flower)" | xargs -r docker rm 2>/dev/null || true

sleep 2

# 1. Start Airflow PostgreSQL Database
echo ""
echo "📦 Starting Airflow specific PostgreSQL database..."
docker run --name dev-airflow-postgres -d \
  -p 5433:5432 \
  -e POSTGRES_DB=airflow \
  -e POSTGRES_USER=airflow \
  -e POSTGRES_PASSWORD=airflow \
  postgres:13

echo "⏳ Waiting for database to start..."
sleep 15

# 2. Start Airflow Redis
echo ""
echo "🔴 Starting Airflow specific Redis..."
docker run --name dev-airflow-redis -d \
  -p 6380:6379 \
  redis:7-alpine redis-server --requirepass airflow

echo "⏳ Waiting for Redis to start..."
sleep 10

# 3. Initialize Airflow Database
echo ""
echo "⚙️  Initializing Airflow database..."
docker run --name dev-airflow-init -d \
  --link dev-airflow-postgres:postgres \
  -e AIRFLOW__CORE__EXECUTOR=LocalExecutor \
  -e AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow \
  -e AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags \
  -e AIRFLOW__CORE__LOAD_EXAMPLES=true \
  -e AIRFLOW_UID=1000 \
  --rm \
  full-stack-fastapi-template-official-orgrag-airflow-init:latest

echo "⏳ Waiting for database initialization to complete..."
sleep 30

# 4. Start Airflow Web Server
echo ""
echo "🌐 Starting Airflow Web Server..."
docker run --name dev-airflow-webserver -d \
  -p 9090:8080 \
  --link dev-airflow-postgres:postgres \
  --link dev-airflow-redis:redis \
  -e AIRFLOW__CORE__EXECUTOR=LocalExecutor \
  -e AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow \
  -e AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags \
  -e AIRFLOW__WEBSERVER_SECRET_KEY=changethis \
  -e AIRFLOW_UID=1000 \
  -e _AIRFLOW_WWW_USER_USERNAME=airflow \
  -e _AIRFLOW_WWW_USER_PASSWORD=airflow \
  full-stack-fastapi-template-official-orgrag-airflow-webserver:latest

echo "⏳ Waiting for Web Server to start..."
sleep 20

# 5. Start Airflow Scheduler
echo ""
echo "📅 Starting Airflow Scheduler..."
docker run --name dev-airflow-scheduler -d \
  --link dev-airflow-postgres:postgres \
  --link dev-airflow-redis:redis \
  -e AIRFLOW__CORE__EXECUTOR=LocalExecutor \
  -e AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow \
  -e AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags \
  -e AIRFLOW_UID=1000 \
  full-stack-fastapi-template-official-orgrag-airflow-scheduler:latest

echo "⏳ Waiting for Scheduler to start..."
sleep 15

# 6. Start Airflow Worker
echo ""
echo "👷 Starting Airflow Worker..."
docker run --name dev-airflow-worker -d \
  --link dev-airflow-postgres:postgres \
  --link dev-airflow-redis:redis \
  -e AIRFLOW__CORE__EXECUTOR=LocalExecutor \
  -e AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow \
  -e AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags \
  -e AIRFLOW_UID=1000 \
  full-stack-fastapi-template-official-orgrag-airflow-worker:latest

echo "⏳ Waiting for Worker to start..."
sleep 15

# 7. Start Flower Monitoring Interface
echo ""
echo "🌺 Starting Flower monitoring interface..."
docker run --name dev-airflower -d \
  -p 5555:5555 \
  --link dev-airflow-postgres:postgres \
  --link dev-airflow-redis:redis \
  -e AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags \
  -e FLOWER_PORT=5555 \
  -e AIRFLOW_UID=1000 \
  full-stack-fastapi-template-official-orgrag-flower:latest

echo "⏳ Waiting for Flower to start..."
sleep 20

# Check services status
echo ""
echo "📊 Airflow Services Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(airflow|flower)"

echo ""
echo "✅ Airflow Services Startup Complete!"
echo ""
echo "🌐 Access Addresses:"
echo "  📌 Airflow Web UI: http://localhost:9090"
echo "  📌 Flower UI: http://localhost:5555"
echo "  📌 Default User: airflow / airflow"
echo ""
echo "📝 View Logs:"
echo "    docker logs dev-airflow-webserver --tail 50 -f"
echo "    docker logs dev-airflow-scheduler --tail 50 -f"
echo "    docker logs dev-airflow-worker --tail 50 -f"
echo "    docker logs dev-airflower --tail 50 -f"
echo ""
echo "🛑 Stop Airflow Services: ./bin/stop-airflow-manual.sh"
echo ""
