# OP_CMS Docker Scripts

This directory contains deployment and maintenance scripts for OP_CMS.

## Scripts

### deploy.sh
Main deployment script for production environment.

**Usage:**
```bash
# Full deployment
./deploy.sh deploy

# Build images only
./deploy.sh build

# Start services
./deploy.sh start

# View status
./deploy.sh status

# View logs
./deploy.sh logs [service_name]

# Stop services
./deploy.sh stop

# Restart services
./deploy.sh restart

# Clean up (WARNING: removes all data)
./deploy.sh clean

# Health check
./deploy.sh health
```

### health-check.sh
Health check script that verifies all services are running correctly.

**Usage:**
```bash
./health-check.sh
```

### view-logs.sh
View and filter logs from services.

**Usage:**
```bash
# View all logs
./view-logs.sh

# View backend logs
./view-logs.sh -s backend

# Follow logs
./view-logs.sh -s backend -f

# Show last 200 lines
./view-logs.sh -s backend -n 200

# Filter by log level
./view-logs.sh -s backend -l ERROR
```

### init-db.sh
Initialize the database with required tables and sample data.

**Usage:**
```bash
./init-db.sh
```

## Making Scripts Executable

Run this command to make all scripts executable:
```bash
chmod +x docker/scripts/*.sh
```

## Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your settings

# 2. Make scripts executable
chmod +x docker/scripts/*.sh

# 3. Deploy
./docker/scripts/deploy.sh deploy

# 4. Verify
./docker/scripts/deploy.sh health

# 5. View logs
./docker/scripts/view-logs.sh -f
```
