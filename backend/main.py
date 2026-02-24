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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Sanic app
app = Sanic("OP_CMS")

# Enable CORS
CORS(app)

# Register blueprints
app.blueprint(customer_bp)

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
    logger.info("Registered endpoints:")
    logger.info("  - GET  /health")
    logger.info("  - GET  /")
    logger.info("  - GET  /api/v1/customers")
    logger.info("  - POST /api/v1/customers")
    logger.info("  - GET  /api/v1/customers/<customer_id>")
    logger.info("  - PUT  /api/v1/customers/<customer_id>")
    logger.info("  - DELETE /api/v1/customers/<customer_id>")
    logger.info("  - GET  /api/v1/customers/check-duplicate")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
