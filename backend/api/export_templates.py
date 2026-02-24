# OP_CMS Export Templates API
# Story 6.3: Export Template Management

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest, Forbidden
from typing import Optional
import logging
from datetime import datetime

from backend.models.database_models import User
from backend.dao.database_dao import DatabaseSessionFactory
from backend.utils.jwt import require_auth

logger = logging.getLogger(__name__)

export_templates_bp = Blueprint('export_templates', url_prefix='/export-templates')

# In-memory template storage (replace with database in production)
templates_db = {}
template_counter = 0


@export_templates_bp.route('', methods=['POST'])
@require_auth
async def create_template(req: request.Request):
    """
    Create export template
    
    Request Body:
    {
        "name": "Customer Export Template",
        "description": "Export customer data with basic fields",
        "resource_type": "customer",  // customer, settlement, payment
        "fields": ["company_name", "contact_name", "contact_phone"],
        "format": "excel",  // excel, csv
        "filters": {...},  // optional default filters
        "is_shared": false
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "template": {...}
        }
    }
    """
    try:
        global template_counter
        
        data = req.json
        
        # Validate required fields
        required_fields = ['name', 'resource_type', 'fields', 'format']
        for field in required_fields:
            if not data.get(field):
                return json({
                    'success': False,
                    'error': 'Missing required fields',
                    'message': f'{field} is required'
                }, status=400)
        
        # Get current user
        current_user = getattr(req, 'current_user', {})
        user_id = current_user.get('user_id')
        
        if not user_id:
            return json({
                'success': False,
                'error': 'Authentication required',
                'message': 'User not authenticated'
            }, status=401)
        
        # Create template
        template_counter += 1
        template_id = template_counter
        
        template = {
            'id': template_id,
            'name': data['name'],
            'description': data.get('description', ''),
            'resource_type': data['resource_type'],
            'fields': data['fields'],
            'format': data['format'],
            'filters': data.get('filters', {}),
            'is_shared': data.get('is_shared', False),
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        templates_db[template_id] = template
        
        return json({
            'success': True,
            'data': {
                'template': template
            },
            'message': 'Template created successfully'
        }, status=201)
        
    except Exception as e:
        logger.error(f"Failed to create template: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@export_templates_bp.route('', methods=['GET'])
@require_auth
async def list_templates(req: request.Request):
    """
    List export templates
    
    Query Parameters:
    - resource_type: Filter by resource type
    - include_shared: Include shared templates (default: true)
    
    Returns:
    {
        "success": true,
        "data": {
            "templates": [...],
            "total": 10
        }
    }
    """
    try:
        # Get current user
        current_user = getattr(req, 'current_user', {})
        user_id = current_user.get('user_id')
        
        if not user_id:
            return json({
                'success': False,
                'error': 'Authentication required',
                'message': 'User not authenticated'
            }, status=401)
        
        # Parse query parameters
        resource_type = req.args.get('resource_type', '')
        include_shared = req.args.get('include_shared', 'true').lower() == 'true'
        
        # Filter templates
        templates = []
        for template in templates_db.values():
            # Filter by user_id or is_shared
            if template['user_id'] == user_id or (include_shared and template['is_shared']):
                # Filter by resource_type if specified
                if not resource_type or template['resource_type'] == resource_type:
                    templates.append(template)
        
        return json({
            'success': True,
            'data': {
                'templates': templates,
                'total': len(templates)
            },
            'message': 'Templates retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to list templates: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@export_templates_bp.route('/<template_id:int>', methods=['GET'])
@require_auth
async def get_template(req: request.Request, template_id: int):
    """
    Get template by ID
    
    Returns:
    {
        "success": true,
        "data": {
            "template": {...}
        }
    }
    """
    try:
        template = templates_db.get(template_id)
        
        if not template:
            raise NotFound("Template not found")
        
        # Check permissions
        current_user = getattr(req, 'current_user', {})
        user_id = current_user.get('user_id')
        
        if template['user_id'] != user_id and not template['is_shared']:
            raise Forbidden("You don't have permission to view this template")
        
        return json({
            'success': True,
            'data': {
                'template': template
            },
            'message': 'Template retrieved successfully'
        })
        
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to get template: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@export_templates_bp.route('/<template_id:int>', methods=['PUT'])
@require_auth
async def update_template(req: request.Request, template_id: int):
    """
    Update template
    
    Request Body:
    {
        "name": "Updated Template Name",
        "description": "Updated description",
        "fields": [...],
        "is_shared": true
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "template": {...}
        }
    }
    """
    try:
        template = templates_db.get(template_id)
        
        if not template:
            raise NotFound("Template not found")
        
        # Check permissions
        current_user = getattr(req, 'current_user', {})
        user_id = current_user.get('user_id')
        
        if template['user_id'] != user_id:
            raise Forbidden("You don't have permission to update this template")
        
        data = req.json
        
        # Update fields
        if 'name' in data:
            template['name'] = data['name']
        if 'description' in data:
            template['description'] = data['description']
        if 'fields' in data:
            template['fields'] = data['fields']
        if 'format' in data:
            template['format'] = data['format']
        if 'filters' in data:
            template['filters'] = data['filters']
        if 'is_shared' in data:
            template['is_shared'] = data['is_shared']
        
        template['updated_at'] = datetime.utcnow().isoformat()
        
        return json({
            'success': True,
            'data': {
                'template': template
            },
            'message': 'Template updated successfully'
        })
        
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to update template: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@export_templates_bp.route('/<template_id:int>', methods=['DELETE'])
@require_auth
async def delete_template(req: request.Request, template_id: int):
    """
    Delete template
    
    Returns:
    {
        "success": true,
        "message": "Template deleted successfully"
    }
    """
    try:
        template = templates_db.get(template_id)
        
        if not template:
            raise NotFound("Template not found")
        
        # Check permissions
        current_user = getattr(req, 'current_user', {})
        user_id = current_user.get('user_id')
        
        if template['user_id'] != user_id:
            raise Forbidden("You don't have permission to delete this template")
        
        del templates_db[template_id]
        
        return json({
            'success': True,
            'message': 'Template deleted successfully'
        })
        
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to delete template: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@export_templates_bp.route('/<template_id:int>/apply', methods=['POST'])
@require_auth
async def apply_template(req: request.Request, template_id: int):
    """
    Apply template to export
    
    Request Body:
    {
        "filters": {...},  // optional additional filters
        "override_fields": [...]  // optional field overrides
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "fields": [...],
            "format": "excel",
            "filters": {...}
        }
    }
    """
    try:
        template = templates_db.get(template_id)
        
        if not template:
            raise NotFound("Template not found")
        
        # Check permissions
        current_user = getattr(req, 'current_user', {})
        user_id = current_user.get('user_id')
        
        if template['user_id'] != user_id and not template['is_shared']:
            raise Forbidden("You don't have permission to use this template")
        
        data = req.json or {}
        
        # Get template configuration
        fields = data.get('override_fields', template['fields'])
        export_format = data.get('format', template['format'])
        
        # Merge filters (template filters + additional filters)
        filters = template['filters'].copy()
        if 'filters' in data:
            filters.update(data['filters'])
        
        return json({
            'success': True,
            'data': {
                'template_id': template_id,
                'template_name': template['name'],
                'resource_type': template['resource_type'],
                'fields': fields,
                'format': export_format,
                'filters': filters
            },
            'message': 'Template applied successfully'
        })
        
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to apply template: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
