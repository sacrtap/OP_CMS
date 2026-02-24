# OP_CMS Pricing Configuration API
# Story 2.1: Single-tier Pricing Management

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest, Unauthorized
from typing import Optional
from sqlalchemy import or_, and_
import logging

from backend.models.database_models import (
    PriceConfig, PriceConfigCreate, PriceConfigUpdate, 
    PriceConfigResponse, PriceConfigListResponse
)
from backend.dao.database_dao import DatabaseSessionFactory

logger = logging.getLogger(__name__)

pricing_bp = Blueprint('pricing', url_prefix='/api/v1/pricing')


@pricing_bp.route('', methods=['GET'])
async def list_pricing_configs(req: request.Request):
    """
    List pricing configurations with pagination and filtering
    
    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - customer_id: Filter by customer_id
    - device_series: Filter by device_series (X/N/L)
    - price_model: Filter by price_model (single/multi/tiered)
    - is_active: Filter by active status
    - search: Search term (config name)
    
    Returns:
    - Pricing configurations with pagination metadata
    """
    try:
        # Parse query parameters
        page = max(1, int(req.args.get('page', 1)))
        page_size = min(100, max(1, int(req.args.get('page_size', 20))))
        customer_id = req.args.get('customer_id', '')
        device_series = req.args.get('device_series', '')
        price_model = req.args.get('price_model', '')
        is_active = req.args.get('is_active', '')
        search = req.args.get('search', '')
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Build query with filters
            query = session.query(PriceConfig)
            
            if customer_id:
                query = query.filter(PriceConfig.customer_id == int(customer_id))
            
            if device_series:
                query = query.filter(PriceConfig.device_series == device_series)
            
            if price_model:
                query = query.filter(PriceConfig.price_model == price_model)
            
            if is_active:
                is_active_bool = is_active.lower() == 'true'
                query = query.filter(PriceConfig.is_active == is_active_bool)
            
            if search:
                search_term = f'%{search}%'
                query = query.filter(PriceConfig.name.like(search_term))
            
            # Get total count
            total = query.count()
            
            # Get paginated results
            configs = query.order_by(PriceConfig.created_at.desc()).offset(offset).limit(page_size).all()
            
            # Calculate total pages
            total_pages = (total + page_size - 1) // page_size
            
            # Convert to response format
            config_responses = [
                PriceConfigResponse(
                    id=c.id,
                    config_id=c.config_id,
                    customer_id=c.customer_id,
                    name=c.name,
                    description=c.description,
                    price_model=c.price_model,
                    device_series=c.device_series,
                    currency=c.currency,
                    min_quantity=c.min_quantity,
                    max_quantity=c.max_quantity,
                    unit_price=c.unit_price,
                    base_price=c.base_price,
                    volume_discount=c.volume_discount,
                    pricing_rules=c.pricing_rules,
                    is_active=c.is_active,
                    created_at=c.created_at,
                    updated_at=c.updated_at
                ) for c in configs
            ]
            
            response_data = PriceConfigListResponse(
                configs=config_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
            return json({
                'success': True,
                'data': response_data.model_dump(),
                'message': f'Retrieved {len(config_responses)} pricing configs'
            })
            
        finally:
            session.close()
            
    except ValueError as e:
        logger.error(f"Invalid parameter: {str(e)}")
        return json({
            'success': False,
            'error': 'Invalid parameter',
            'message': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to list pricing configs: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@pricing_bp.route('', methods=['POST'])
async def create_pricing_config(req: request.Request):
    """
    Create new pricing configuration
    
    Request Body:
    {
        "customer_id": int (required),
        "name": string (required),
        "description": string (optional),
        "price_model": "single"|"multi"|"tiered" (required),
        "device_series": "X"|"N"|"L" (required),
        "currency": string (optional, default: CNY),
        "min_quantity": decimal (optional),
        "max_quantity": decimal (optional),
        "unit_price": decimal (required for single-tier),
        "base_price": decimal (optional),
        "volume_discount": decimal (optional),
        "pricing_rules": dict (optional),
        "is_active": boolean (optional, default: true)
    }
    
    Returns:
    - Created pricing configuration
    """
    try:
        data = req.json
        
        # Validate required fields
        if not data.get('customer_id') or not data.get('name') or not data.get('price_model') or not data.get('device_series'):
            return json({
                'success': False,
                'error': 'Missing required fields',
                'message': 'customer_id, name, price_model, and device_series are required'
            }, status=400)
        
        # Validate price_model
        if data['price_model'] not in ['single', 'multi', 'tiered']:
            return json({
                'success': False,
                'error': 'Invalid price_model',
                'message': 'price_model must be single, multi, or tiered'
            }, status=400)
        
        # Validate device_series
        if data['device_series'] not in ['X', 'N', 'L']:
            return json({
                'success': False,
                'error': 'Invalid device_series',
                'message': 'device_series must be X, N, or L'
            }, status=400)
        
        # Validate unit_price for single-tier pricing
        if data['price_model'] == 'single' and data.get('unit_price') is None:
            return json({
                'success': False,
                'error': 'Missing unit_price',
                'message': 'unit_price is required for single-tier pricing'
            }, status=400)
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Check for duplicate (customer_id + device_series)
            existing = session.query(PriceConfig).filter(
                and_(
                    PriceConfig.customer_id == data['customer_id'],
                    PriceConfig.device_series == data['device_series']
                )
            ).first()
            
            if existing:
                return json({
                    'success': False,
                    'error': 'Duplicate pricing config',
                    'message': 'A pricing config already exists for this customer and device series'
                }, status=409)
            
            # Create new config
            new_config = PriceConfig(
                customer_id=data['customer_id'],
                name=data['name'],
                description=data.get('description'),
                price_model=data['price_model'],
                device_series=data['device_series'],
                currency=data.get('currency', 'CNY'),
                min_quantity=data.get('min_quantity'),
                max_quantity=data.get('max_quantity'),
                unit_price=data.get('unit_price'),
                base_price=data.get('base_price'),
                volume_discount=data.get('volume_discount'),
                pricing_rules=data.get('pricing_rules'),
                is_active=data.get('is_active', True)
            )
            
            session.add(new_config)
            session.commit()
            session.refresh(new_config)
            
            return json({
                'success': True,
                'data': PriceConfigResponse(
                    id=new_config.id,
                    config_id=new_config.config_id,
                    customer_id=new_config.customer_id,
                    name=new_config.name,
                    description=new_config.description,
                    price_model=new_config.price_model,
                    device_series=new_config.device_series,
                    currency=new_config.currency,
                    min_quantity=new_config.min_quantity,
                    max_quantity=new_config.max_quantity,
                    unit_price=new_config.unit_price,
                    base_price=new_config.base_price,
                    volume_discount=new_config.volume_discount,
                    pricing_rules=new_config.pricing_rules,
                    is_active=new_config.is_active,
                    created_at=new_config.created_at,
                    updated_at=new_config.updated_at
                ).model_dump(),
                'message': 'Pricing config created successfully'
            }, status=201)
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to create pricing config: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@pricing_bp.route('/<config_id:int>', methods=['GET'])
async def get_pricing_config(req: request.Request, config_id: int):
    """
    Get pricing configuration by ID
    
    Returns:
    - Pricing configuration details
    """
    try:
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            config = session.query(PriceConfig).filter(PriceConfig.id == config_id).first()
            
            if not config:
                return json({
                    'success': False,
                    'error': 'Not found',
                    'message': 'Pricing config not found'
                }, status=404)
            
            return json({
                'success': True,
                'data': PriceConfigResponse(
                    id=config.id,
                    config_id=config.config_id,
                    customer_id=config.customer_id,
                    name=config.name,
                    description=config.description,
                    price_model=config.price_model,
                    device_series=config.device_series,
                    currency=config.currency,
                    min_quantity=config.min_quantity,
                    max_quantity=config.max_quantity,
                    unit_price=config.unit_price,
                    base_price=config.base_price,
                    volume_discount=config.volume_discount,
                    pricing_rules=config.pricing_rules,
                    is_active=config.is_active,
                    created_at=config.created_at,
                    updated_at=config.updated_at
                ).model_dump()
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to get pricing config: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@pricing_bp.route('/<config_id:int>', methods=['PUT'])
async def update_pricing_config(req: request.Request, config_id: int):
    """
    Update pricing configuration
    
    Request Body (all fields optional):
    {
        "name": string,
        "description": string,
        "price_model": "single"|"multi"|"tiered",
        "device_series": "X"|"N"|"L",
        "currency": string,
        "min_quantity": decimal,
        "max_quantity": decimal,
        "unit_price": decimal,
        "base_price": decimal,
        "volume_discount": decimal,
        "pricing_rules": dict,
        "is_active": boolean
    }
    
    Returns:
    - Updated pricing configuration
    """
    try:
        data = req.json
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            config = session.query(PriceConfig).filter(PriceConfig.id == config_id).first()
            
            if not config:
                return json({
                    'success': False,
                    'error': 'Not found',
                    'message': 'Pricing config not found'
                }, status=404)
            
            # Update fields (only provided fields)
            if 'name' in data:
                config.name = data['name']
            if 'description' in data:
                config.description = data['description']
            if 'price_model' in data:
                if data['price_model'] not in ['single', 'multi', 'tiered']:
                    return json({
                        'success': False,
                        'error': 'Invalid price_model',
                        'message': 'price_model must be single, multi, or tiered'
                    }, status=400)
                config.price_model = data['price_model']
            if 'device_series' in data:
                if data['device_series'] not in ['X', 'N', 'L']:
                    return json({
                        'success': False,
                        'error': 'Invalid device_series',
                        'message': 'device_series must be X, N, or L'
                    }, status=400)
                config.device_series = data['device_series']
            if 'currency' in data:
                config.currency = data['currency']
            if 'min_quantity' in data:
                config.min_quantity = data['min_quantity']
            if 'max_quantity' in data:
                config.max_quantity = data['max_quantity']
            if 'unit_price' in data:
                config.unit_price = data['unit_price']
            if 'base_price' in data:
                config.base_price = data['base_price']
            if 'volume_discount' in data:
                config.volume_discount = data['volume_discount']
            if 'pricing_rules' in data:
                config.pricing_rules = data['pricing_rules']
            if 'is_active' in data:
                config.is_active = data['is_active']
            
            session.commit()
            session.refresh(config)
            
            return json({
                'success': True,
                'data': PriceConfigResponse(
                    id=config.id,
                    config_id=config.config_id,
                    customer_id=config.customer_id,
                    name=config.name,
                    description=config.description,
                    price_model=config.price_model,
                    device_series=config.device_series,
                    currency=config.currency,
                    min_quantity=config.min_quantity,
                    max_quantity=config.max_quantity,
                    unit_price=config.unit_price,
                    base_price=config.base_price,
                    volume_discount=config.volume_discount,
                    pricing_rules=config.pricing_rules,
                    is_active=config.is_active,
                    created_at=config.created_at,
                    updated_at=config.updated_at
                ).model_dump(),
                'message': 'Pricing config updated successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to update pricing config: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@pricing_bp.route('/<config_id:int>', methods=['DELETE'])
async def delete_pricing_config(req: request.Request, config_id: int):
    """
    Delete pricing configuration
    
    Returns:
    - Success message
    """
    try:
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            config = session.query(PriceConfig).filter(PriceConfig.id == config_id).first()
            
            if not config:
                return json({
                    'success': False,
                    'error': 'Not found',
                    'message': 'Pricing config not found'
                }, status=404)
            
            session.delete(config)
            session.commit()
            
            return json({
                'success': True,
                'message': 'Pricing config deleted successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to delete pricing config: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
