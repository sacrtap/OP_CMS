#!/bin/bash
# OP_CMS Health Check Script
# This script checks the health of all services

set -e

echo "=== OP_CMS Health Check ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service health
check_service() {
    local service_name=$1
    local health_cmd=$2
    
    if eval "$health_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $service_name is healthy"
        return 0
    else
        echo -e "${RED}✗${NC} $service_name is NOT healthy"
        return 1
    fi
}

# Check MySQL
echo "Checking MySQL..."
if check_service "MySQL" "docker exec op_cms_mysql mysqladmin ping -h localhost -u root -prootpassword"; then
    mysql_status=0
else
    mysql_status=1
fi

# Check Redis
echo "Checking Redis..."
if check_service "Redis" "docker exec op_cms_redis redis-cli -a SecureRedisPassword789! ping"; then
    redis_status=0
else
    redis_status=1
fi

# Check Backend
echo "Checking Backend API..."
if check_service "Backend" "curl -f -s http://localhost:8000/health"; then
    backend_status=0
else
    backend_status=1
fi

# Check Frontend
echo "Checking Frontend..."
if check_service "Frontend" "curl -f -s http://localhost/"; then
    frontend_status=0
else
    frontend_status=1
fi

echo ""
echo "=== Health Check Summary ==="

total_failed=$((mysql_status + redis_status + backend_status + frontend_status))

if [ $total_failed -eq 0 ]; then
    echo -e "${GREEN}All services are healthy!${NC}"
    exit 0
else
    echo -e "${RED}$total_failed service(s) failed health check${NC}"
    exit 1
fi
