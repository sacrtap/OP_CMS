# OP_CMS System Parameters API
# Story 7.1: System Parameter Configuration

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest, Forbidden
from typing import Optional
import logging

from backend.models.database_models import SystemParameter
from backend.dao.database_dao import DatabaseSessionFactory
from backend.utils.jwt import require_auth, require_role

logger = logging.getLogger(__name__)

system_parameters_bp = Blueprint('system_parameters', url_prefix='/system-parameters')


@system_parameters_bp.route('', methods=['GET'])
@require_auth
@require_role('admin')
async def list_system_parameters(req: request.Request):
    """
    List system parameters
    
    Query Parameters:
    - category: Filter by category (settlement, warning, import, export, general)
    
    Returns:
    {
        "success": true,
        "data": {
            "parameters": [...],
            "total": 10
        }
    }
    """
    try:
        category = req.args.get('category', '')
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Build query
            query = session.query(SystemParameter)
            
            if category:
                query = query.filter(SystemParameter.category == category)
            
            parameters = query.all()
            
            return json({
                'success': True,
                'data': {
                    'parameters': [p.to_dict() for p in parameters],
                    'total': len(parameters)
                },
                'message': 'System parameters retrieved successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to list system parameters: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@system_parameters_bp.route('/<param_key>', methods=['GET'])
@require_auth
async def get_system_parameter(req: request.Request, param_key: str):
    """
    Get system parameter by key
    
    Returns:
    {
        "success": true,
        "data": {
            "parameter": {...}
        }
    }
    """
    try:
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            parameter = session.query(SystemParameter).filter(SystemParameter.key == param_key).first()
            
            if not parameter:
                raise NotFound("Parameter not found")
            
            return json({
                'success': True,
                'data': {
                    'parameter': parameter.to_dict()
                },
                'message': 'Parameter retrieved successfully'
            })
            
        finally:
            session.close()
            
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to get system parameter: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@system_parameters_bp.route('/<param_key>', methods=['PUT'])
@require_auth
@require_role('admin')
async def update_system_parameter(req: request.Request, param_key: str):
    """
    Update system parameter
    
    Request Body:
    {
        "value": "30",
        "description": "Overdue warning threshold in days"
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "parameter": {...}
        }
    }
    """
    try:
        data = req.json
        
        if 'value' not in data:
            return json({
                'success': False,
                'error': 'Missing required fields',
                'message': 'value is required'
            }, status=400)
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            parameter = session.query(SystemParameter).filter(SystemParameter.key == param_key).first()
            
            if not parameter:
                raise NotFound("Parameter not found")
            
            # Update value
            parameter.set_typed_value(data['value'])
            
            # Update description if provided
            if 'description' in data:
                parameter.description = data['description']
            
            # Update user
            current_user = getattr(req, 'current_user', {})
            parameter.updated_by = current_user.get('user_id')
            
            session.commit()
            session.refresh(parameter)
            
            return json({
                'success': True,
                'data': {
                    'parameter': parameter.to_dict()
                },
                'message': 'Parameter updated successfully'
            })
            
        finally:
            session.close()
            
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to update system parameter: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@system_parameters_bp.route('/initialize', methods=['POST'])
@require_auth
@require_role('admin')
async def initialize_system_parameters(req: request.Request):
    """
    Initialize default system parameters
    
    Returns:
    {
        "success": true,
        "data": {
            "parameters": [...]
        }
    }
    """
    try:
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Define default parameters
            default_parameters = [
                # Settlement parameters
                {'key': 'settlement_cycle', 'value': 'monthly', 'value_type': 'string', 'description': 'Settlement cycle: daily, weekly, monthly, quarterly, yearly', 'category': 'settlement'},
                {'key': 'settlement_day', 'value': '1', 'value_type': 'integer', 'description': 'Day of month for settlement (1-28)', 'category': 'settlement'},
                
                # Warning parameters
                {'key': 'overdue_warning_days', 'value': '30', 'value_type': 'integer', 'description': 'Days before payment is considered overdue', 'category': 'warning'},
                {'key': 'overdue_critical_days', 'value': '60', 'value_type': 'integer', 'description': 'Days before payment is critically overdue', 'category': 'warning'},
                {'key': 'churn_warning_days', 'value': '90', 'value_type': 'integer', 'description': 'Days of inactivity before customer is at risk of churning', 'category': 'warning'},
                
                # Import parameters
                {'key': 'import_max_rows', 'value': '10000', 'value_type': 'integer', 'description': 'Maximum number of rows per import', 'category': 'import'},
                {'key': 'import_allow_update', 'value': 'true', 'value_type': 'boolean', 'description': 'Allow updating existing records during import', 'category': 'import'},
                
                # Export parameters
                {'key': 'export_max_rows', 'value': '100000', 'value_type': 'integer', 'description': 'Maximum number of rows per export', 'category': 'export'},
                {'key': 'export_format', 'value': 'excel', 'value_type': 'string', 'description': 'Default export format: excel, csv', 'category': 'export'},
                
                # General parameters
                {'key': 'system_name', 'value': 'OP_CMS', 'value_type': 'string', 'description': 'System name', 'category': 'general'},
                {'key': 'timezone', 'value': 'Asia/Shanghai', 'value_type': 'string', 'description': 'System timezone', 'category': 'general'}
            ]
            
            created = []
            updated = []
            
            for param_data in default_parameters:
                parameter = session.query(SystemParameter).filter(SystemParameter.key == param_data['key']).first()
                
                if parameter:
                    # Update existing
                    parameter.set_typed_value(param_data['value'])
                    parameter.description = param_data['description']
                    parameter.category = param_data['category']
                    updated.append(param_data['key'])
                else:
                    # Create new
                    parameter = SystemParameter(
                        key=param_data['key'],
                        value_type=param_data['value_type'],
                        description=param_data['description'],
                        category=param_data['category']
                    )
                    parameter.set_typed_value(param_data['value'])
                    session.add(parameter)
                    created.append(param_data['key'])
            
            session.commit()
            
            return json({
                'success': True,
                'data': {
                    'created': created,
                    'updated': updated,
                    'total': len(created) + len(updated)
                },
                'message': f'System parameters initialized: {len(created)} created, {len(updated)} updated'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to initialize system parameters: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
