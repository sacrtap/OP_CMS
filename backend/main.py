# OP_CMS Backend Main Application
# Sanic Server Entry Point

"""
OP_CMS Backend Server - Sanic Framework

Usage:
    python -m sanic backend.main:app --host 0.0.0.0 --port 8000
    
Development:
    python -m sanic backend.main:app --host 0.0.0.0 --port 8000 --debug --auto-reload
"""

from sanic import Sanic
from sanic_cors import CORS
from sanic_ext import Extend
import logging

from backend.api.customers import customer_bp
from backend.api.auth import auth_bp
from backend.api.pricing import pricing_bp
from backend.api.settlements import settlement_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Sanic app
app = Sanic("OP_CMS")

# Configure Sanic Extensions (OpenAPI/Swagger)
Extend(app).config(
    openapi=True,
    cors=True,
    swagger_ui=True,
    oas_uri_to_json=True,
    oas_autodoc=True
)

# Configure OpenAPI
app.config.OAS = True
app.config.OAS_URI_TO_JSON = "/api/v1/openapi.json"
app.config.OAS_UI = "/api/v1/docs"
app.config.OAS_VERSION = "3.0.0"
app.config.OAS_TITLE = "OP_CMS API Documentation"
app.config.OAS_DESCRIPTION = """
# OP_CMS Backend API

## Overview
OP_CMS (Operations Management System) provides RESTful APIs for:
- Customer Management (CRUD operations)
- Pricing Configuration (Single-tier, Multi-tier, Tiered pricing)
- Settlement Records
- User Authentication & Authorization (JWT)

## Authentication
Most endpoints require authentication using JWT Bearer tokens.

```
Authorization: Bearer <your_jwt_token>
```

## Base URL
```
Production: https://api.op-cms.com
Development: http://localhost:8000
```
"""
app.config.OAS_CONTACT_NAME = "OP_CMS Team"
app.config.OAS_CONTACT_EMAIL = "support@op-cms.com"
app.config.OAS_LICENSE_NAME = "MIT"

# Enable CORS
CORS(app)

# Register blueprints
app.blueprint(customer_bp, url_prefix="/api/v1")
app.blueprint(auth_bp, url_prefix="/api/v1")
app.blueprint(pricing_bp, url_prefix="/api/v1")
app.blueprint(settlement_bp, url_prefix="/api/v1")

# Health check endpoint
@app.route('/health', methods=['GET'])
async def health_check(request):
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'OP_CMS Backend',
        'version': '1.0.0'
    }

# Root endpoint
@app.route('/', methods=['GET'])
async def root(request):
    """Root endpoint"""
    return {
        'service': 'OP_CMS Backend API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'customers': '/api/v1/customers',
            'api_docs': '/api/v1/docs'
        }
    }

@app.before_server_start
async def before_server_start(app, loop):
    """Initialize before server starts"""
    logger.info("Starting OP_CMS Backend Server...")
    logger.info("="*60)
    logger.info("Service Information:")
    logger.info(f"  - Name: OP_CMS Backend API")
    logger.info(f"  - Version: 1.0.0")
    logger.info(f"  - Port: 8000")
    logger.info("="*60)
    logger.info("Registered Endpoints:")
    logger.info("  Authentication:")
    logger.info("    - POST   /api/v1/auth/register")
    logger.info("    - POST   /api/v1/auth/login")
    logger.info("    - POST   /api/v1/auth/refresh")
    logger.info("    - GET    /api/v1/auth/me")
    logger.info("    - POST   /api/v1/auth/logout")
    logger.info("  Customer Management:")
    logger.info("    - GET    /api/v1/customers")
    logger.info("    - POST   /api/v1/customers")
    logger.info("    - GET    /api/v1/customers/<customer_id>")
    logger.info("    - PUT    /api/v1/customers/<customer_id>")
    logger.info("    - DELETE /api/v1/customers/<customer_id>")
    logger.info("    - GET    /api/v1/customers/check-duplicate")
    logger.info("  API Documentation:")
    logger.info("    - GET    /api/v1/docs (Swagger UI)")
    logger.info("    - GET    /api/v1/openapi.json (OpenAPI spec)")
    logger.info("="*60)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
