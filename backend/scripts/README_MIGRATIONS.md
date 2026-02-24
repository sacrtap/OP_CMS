# OP_CMS Database Scripts

## Migration Scripts

### Setup Alembic (One-time)

```bash
# Install alembic
pip install alembic

# Already initialized in backend/migrations/
```

### Run Migrations

```bash
# Upgrade database to latest version
cd backend
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade 001_initial

# View current version
alembic current

# View migration history
alembic history
```

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration
alembic revision -m "Add new column"
```

## Seed Data

### Run Seed Script

```bash
# Seed database with initial data
python backend/scripts/seed_data.py

# This creates:
# - Admin user (admin/Admin123!)
# - Operator user (operator/Operator123!)
# - 2 demo customers
```

### Default Credentials

After running seed script:

**Admin Account:**
- Username: `admin`
- Password: `Admin123!`
- Role: admin (full access)

**Operator Account:**
- Username: `operator`
- Password: `Operator123!`
- Role: operator (standard access)

⚠️ **IMPORTANT:** Change these passwords in production!

## Database Connection

Default connection string (update in alembic.ini):
```
mysql+pymysql://op_cms_user:CHANGE_ME@localhost:3306/op_cms
```

## Tables Created

After running migrations:

1. **customers** - Customer information (18 fields)
2. **price_configs** - Pricing configurations
3. **settlement_records** - Settlement records
4. **users** - User accounts (authentication)
5. **access_logs** - Access audit logs
6. **customer_access** - Customer-level permissions

## Indexes Created

- Customer search indexes (company_name, contact_name, credit_code)
- Customer filter indexes (status, level, province)
- Pricing indexes (customer_id, device_series)
- Settlement indexes (customer_id, period, status)
- User indexes (username, role)
- Access log indexes (user_id, created_at)

Total: 20+ indexes for query optimization
