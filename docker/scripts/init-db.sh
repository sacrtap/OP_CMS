#!/bin/bash
# OP_CMS Database Initialization Helper
# This script helps initialize the database in Docker environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== OP_CMS Database Initialization ==="
echo ""

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
fi

echo "Connecting to MySQL container..."
docker exec -i op_cms_mysql mysql -u root -p${MYSQL_ROOT_PASSWORD:-rootpassword} ${MYSQL_DATABASE:-op_cms} <<EOF
-- Check if tables exist
SHOW TABLES;
EOF

echo ""
echo "Running database initialization script..."
docker exec -it op_cms_backend python backend/scripts/init_db.py

echo ""
echo "Database initialization completed!"
