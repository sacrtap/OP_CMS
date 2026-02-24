# OP_CMS Docker Deployment Guide

Complete guide for deploying OP_CMS using Docker and Docker Compose.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- 10GB disk space

## Quick Start

### 1. Clone and Configure

```bash
# Clone repository
cd /path/to/OP_CMS

# Copy environment template
cp .env.example .env

# Edit configuration
vim .env
```

**Required environment variables:**
- `MYSQL_ROOT_PASSWORD` - MySQL root password
- `MYSQL_DATABASE` - Database name (default: op_cms)
- `MYSQL_USER` - Database user
- `MYSQL_PASSWORD` - Database password
- `REDIS_PASSWORD` - Redis password
- `SECRET_KEY` - Application secret key for session encryption and security

### 2. Make scripts executable

```bash
chmod +x docker/scripts/*.sh
```

### 3. Deploy

```bash
# Full deployment
./docker/scripts/deploy.sh deploy

# Or step by step
docker-compose build
docker-compose up -d
./docker/scripts/init-db.sh
```

### 4. Verify

```bash
# Check service status
docker-compose ps

# Run health check
./docker/scripts/deploy.sh health

# View logs
docker-compose logs -f
```

## Development Mode

For local development with hot-reload:

```bash
# Use development compose file
docker-compose -f docker-compose.dev.yml up

# Access services
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# MySQL: localhost:3306
# Redis: localhost:6379
```

## Production Mode

For production deployment:

```bash
# Build optimized images
docker-compose build --no-cache

# Start services
docker-compose up -d

# Initialize database
./docker/scripts/init-db.sh

# Monitor logs
docker-compose logs -f backend
```

## Service URLs

| Service   | URL                    | Port |
|-----------|------------------------|------|
| Frontend  | http://localhost       | 80   |
| Backend   | http://localhost:8000  | 8000 |
| MySQL     | localhost              | 3306 |
| Redis     | localhost              | 6379 |

## Common Commands

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Service management
```bash
# Start service
docker-compose up -d [service_name]

# Stop service
docker-compose stop [service_name]

# Restart service
docker-compose restart [service_name]

# Rebuild service
docker-compose up -d --build [service_name]
```

### Database operations
```bash
# Access MySQL shell
docker exec -it op_cms_mysql mysql -u op_cms_user -p

# Backup database
docker exec op_cms_mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD} op_cms > backup.sql

# Restore database
docker exec -i op_cms_mysql mysql -u root -p${MYSQL_ROOT_PASSWORD} op_cms < backup.sql
```

### Redis operations
```bash
# Access Redis CLI
docker exec -it op_cms_redis redis-cli -a ${REDIS_PASSWORD}

# Monitor Redis
docker exec -it op_cms_redis redis-cli -a ${REDIS_PASSWORD} monitor
```

## Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs [service_name]

# Check service status
docker-compose ps

# Inspect container
docker inspect op_cms_[service_name]
```

### Database connection issues
```bash
# Verify MySQL is running
docker exec op_cms_mysql mysqladmin ping -h localhost

# Check network
docker network inspect op_cms_network
```

### Rebuild from scratch
```bash
# Stop and remove everything
docker-compose down -v --remove-orphans

# Rebuild images
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

## Performance Tuning

### MySQL Optimization
Edit `docker/mysql/my.cnf`:
- `innodb_buffer_pool_size` - Set to 70% of available RAM for dedicated DB
- `max_connections` - Adjust based on expected concurrent users

### Redis Optimization
Edit `docker/redis/redis.conf`:
- `maxmemory` - Set appropriate memory limit
- `maxmemory-policy` - Choose eviction policy (allkeys-lru recommended)

### Backend Optimization
- Enable Gunicorn workers for production
- Configure Celery for async tasks
- Adjust worker count based on CPU cores

## Security Best Practices

1. **Change default passwords** in `.env` file
2. **Enable HTTPS** using reverse proxy (nginx/traefik)
3. **Restrict network access** - only expose necessary ports
4. **Regular updates** - keep Docker images updated
5. **Backup data** - regular automated backups
6. **Monitor logs** - set up log aggregation
7. **Resource limits** - prevent resource exhaustion

```yaml
# Example resource limits in docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

## Monitoring

### Health Checks
All services include health checks:
- Frontend: HTTP check on port 80
- Backend: HTTP check on /health endpoint
- MySQL: mysqladmin ping
- Redis: redis-cli ping

### Metrics
- Check container stats: `docker stats`
- View resource usage: `docker-compose top`

## Backup Strategy

### Automated Backups
Create a cron job for database backups:

```bash
# /etc/cron.d/op_cms_backup
0 2 * * * root /path/to/OP_CMS/docker/scripts/backup.sh
```

### Backup Script Example
```bash
#!/bin/bash
BACKUP_DIR="/backups/op_cms"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup MySQL
docker exec op_cms_mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD} op_cms > $BACKUP_DIR/mysql_$DATE.sql

# Backup Redis (if persistence enabled)
cp /var/lib/docker/volumes/redis_data/_data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete
```

## Support

For issues and questions:
1. Check logs first
2. Review health check status
3. Verify network connectivity
4. Check resource availability
5. Consult documentation

---

**Last Updated:** 2026-02-24
**Version:** 1.0.0
