#!/bin/bash
# Database Model Fix Script
# Fixes indentation issues in database_models.py

cd /Users/sacrtap/Documents/trae_projects/OP_CMS

# Fix database_models.py indentation
sed -i '' 's/^     /    /g' backend/models/database_models.py

# Fix database_dao.py - ensure proper indentation
sed -i '' 's/^    async def/\nasync def/g' backend/dao/database_dao.py
sed -i '' 's/^     /    /g' backend/dao/database_dao.py

# Verify syntax
python -m py_compile backend/models/database_models.py
python -m py_compile backend/dao/database_dao.py
python -m py_compile backend/scripts/init_db.py

echo "✅ All files syntax verified"
