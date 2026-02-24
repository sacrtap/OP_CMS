#!/bin/bash
# OP_CMS Log Viewer Script
# View and manage logs from all services

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
LINES=100
FOLLOW=false
SERVICE=""
LOG_LEVEL=""

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -s, --service SERVICE  View logs for specific service (frontend|backend|mysql|redis|all)"
    echo "  -n, --lines NUM        Number of lines to show (default: 100)"
    echo "  -f, --follow           Follow log output (default: false)"
    echo "  -l, --level LEVEL      Filter by log level (INFO|WARNING|ERROR|DEBUG)"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -s backend -n 50 -f     # Follow backend logs, show last 50 lines"
    echo "  $0 -s all -l ERROR         # Show ERROR logs from all services"
    echo "  $0                         # Show last 100 lines from all services"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--service)
            SERVICE="$2"
            shift 2
            ;;
        -n|--lines)
            LINES="$2"
            shift 2
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -l|--level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Function to view logs
view_logs() {
    local service_name=$1
    local container_name=$2
    local log_path=$3
    
    echo -e "${BLUE}=== $service_name Logs ===${NC}"
    
    if [ "$FOLLOW" = true ]; then
        if [ -n "$LOG_LEVEL" ]; then
            docker logs -f --tail $LINES $container_name 2>&1 | grep --line-buffered "$LOG_LEVEL" || true
        else
            docker logs -f --tail $LINES $container_name
        fi
    else
        if [ -n "$LOG_LEVEL" ]; then
            docker logs --tail $LINES $container_name 2>&1 | grep "$LOG_LEVEL" || true
        else
            docker logs --tail $LINES $container_name
        fi
    fi
    
    echo ""
}

# View logs based on service
case $SERVICE in
    frontend|all|"")
        view_logs "Frontend" "op_cms_frontend" "/var/log/nginx"
        ;;
    backend)
        view_logs "Backend" "op_cms_backend" "/app/logs"
        ;;
    mysql)
        view_logs "MySQL" "op_cms_mysql" "/var/log/mysql"
        ;;
    redis)
        view_logs "Redis" "op_cms_redis" "/data"
        ;;
    *)
        echo "Unknown service: $SERVICE"
        echo "Available services: frontend, backend, mysql, redis, all"
        exit 1
        ;;
esac
