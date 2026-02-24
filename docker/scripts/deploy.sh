#!/bin/bash
# OP_CMS Production Deployment Script
# This script handles the complete deployment process

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="op_cms"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/docker/logs"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check .env file
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_warning ".env file not found. Copying from .env.example..."
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        log_warning "Please update .env file with your configuration"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

build_images() {
    log_info "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build all images
    docker-compose build --no-cache
    
    log_success "Docker images built successfully"
}

start_services() {
    log_info "Starting services..."
    
    cd "$PROJECT_ROOT"
    
    # Start all services
    docker-compose up -d
    
    log_success "Services started"
}

wait_for_services() {
    log_info "Waiting for services to be healthy..."
    
    # Wait for MySQL
    log_info "Waiting for MySQL..."
    timeout=120
    elapsed=0
    while ! docker exec op_cms_mysql mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD} > /dev/null 2>&1; do
        sleep 2
        elapsed=$((elapsed + 2))
        if [ $elapsed -ge $timeout ]; then
            log_error "MySQL failed to start within $timeout seconds"
            return 1
        fi
    done
    log_success "MySQL is ready"
    
    # Wait for Redis
    log_info "Waiting for Redis..."
    while ! docker exec op_cms_redis redis-cli -a ${REDIS_PASSWORD} ping > /dev/null 2>&1; do
        sleep 1
    done
    log_success "Redis is ready"
    
    # Wait for Backend
    log_info "Waiting for Backend API..."
    while ! curl -f -s http://localhost:8000/health > /dev/null 2>&1; do
        sleep 2
    done
    log_success "Backend API is ready"
    
    # Wait for Frontend
    log_info "Waiting for Frontend..."
    while ! curl -f -s http://localhost/ > /dev/null 2>&1; do
        sleep 1
    done
    log_success "Frontend is ready"
}

run_migrations() {
    log_info "Running database migrations..."
    
    # Execute database initialization script
    docker exec op_cms_backend python backend/scripts/init_db.py || {
        log_warning "Database migration failed or already completed"
        return 0
    }
    
    log_success "Database migrations completed"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Run health check
    if [ -x "$SCRIPT_DIR/health-check.sh" ]; then
        "$SCRIPT_DIR/health-check.sh"
    else
        log_warning "Health check script not found, skipping verification"
        return 0
    fi
}

show_status() {
    log_info "Deployment Status:"
    echo ""
    docker-compose ps
    echo ""
    log_info "Access URLs:"
    echo "  Frontend: http://localhost"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    log_info "To view logs:"
    echo "  docker-compose logs -f [service_name]"
    echo "  Available services: frontend, backend, mysql, redis"
}

# Main deployment function
deploy() {
    log_info "Starting OP_CMS deployment..."
    echo ""
    
    check_prerequisites
    echo ""
    
    build_images
    echo ""
    
    start_services
    echo ""
    
    wait_for_services
    echo ""
    
    run_migrations
    echo ""
    
    verify_deployment
    echo ""
    
    show_status
    
    log_success "Deployment completed successfully!"
}

# Handle command line arguments
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    build)
        check_prerequisites
        build_images
        ;;
    start)
        start_services
        wait_for_services
        verify_deployment
        ;;
    status)
        show_status
        ;;
    logs)
        docker-compose logs -f ${2:-}
        ;;
    stop)
        log_info "Stopping all services..."
        docker-compose down
        log_success "Services stopped"
        ;;
    restart)
        log_info "Restarting all services..."
        docker-compose restart
        wait_for_services
        verify_deployment
        show_status
        ;;
    clean)
        log_warning "This will remove all containers, networks, and volumes!"
        read -p "Are you sure? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            docker-compose down -v --remove-orphans
            log_success "Cleanup completed"
        fi
        ;;
    health)
        "$SCRIPT_DIR/health-check.sh"
        ;;
    *)
        echo "Usage: $0 {deploy|build|start|status|logs|stop|restart|clean|health}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Full deployment (build, start, migrate, verify)"
        echo "  build    - Build Docker images only"
        echo "  start    - Start services and wait for health"
        echo "  status   - Show service status"
        echo "  logs     - View logs (optionally specify service)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  clean    - Remove all containers and volumes"
        echo "  health   - Run health check"
        exit 1
        ;;
esac
