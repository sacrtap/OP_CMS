# OP_CMS Settlement API
# Story 3.1: Automated Settlement Generation

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest
from typing import Optional
import logging
from datetime import datetime
from decimal import Decimal

from backend.models.database_models import SettlementRecord, PriceConfig, Customer
from backend.dao.database_dao import DatabaseSessionFactory
from backend.services.settlement_service import SettlementService, SettlementCalculationError

logger = logging.getLogger(__name__)

settlement_bp = Blueprint('settlement', url_prefix='/settlements')


@settlement_bp.route('/generate', methods=['POST'])
async def generate_settlement(req: request.Request):
    """
    Generate settlement for customers
    
    Request Body:
    {
        "period_start": "2026-02-01",
        "period_end": "2026-02-28",
        "customer_ids": [1, 2, 3]  // Optional, if not provided generate for all customers
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "generation_id": "uuid",
            "total_customers": 10,
            "generated": 8,
            "failed": 2,
            "status": "completed"
        }
    }
    """
    try:
        data = req.json
        
        # Validate required fields
        if not data.get('period_start') or not data.get('period_end'):
            return json({
                'success': False,
                'error': 'Missing required fields',
                'message': 'period_start and period_end are required'
            }, status=400)
        
        # Parse dates
        try:
            period_start = datetime.fromisoformat(data['period_start'])
            period_end = datetime.fromisoformat(data['period_end'])
        except ValueError as e:
            return json({
                'success': False,
                'error': 'Invalid date format',
                'message': 'Dates must be in ISO format (YYYY-MM-DD)'
            }, status=400)
        
        # Get customer IDs (optional)
        customer_ids = data.get('customer_ids', [])
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Get customers
            query = session.query(Customer)
            if customer_ids:
                query = query.filter(Customer.id.in_(customer_ids))
            customers = query.all()
            
            # Get settlement service
            settlement_service = SettlementService()
            
            # Generate settlements
            generation_id = f"gen-{datetime.utcnow().isoformat()}"
            generated = 0
            failed = 0
            errors = []
            
            for customer in customers:
                try:
                    # Get customer's pricing config
                    config_query = session.query(PriceConfig).filter(
                        PriceConfig.customer_id == customer.id,
                        PriceConfig.is_active == True
                    )
                    config = config_query.first()
                    
                    if not config:
                        logger.warning(f"No active pricing config for customer {customer.id}")
                        failed += 1
                        errors.append({
                            'customer_id': customer.id,
                            'error': 'No active pricing config'
                        })
                        continue
                    
                    # Calculate usage (simplified - in production, get from usage data source)
                    usage_quantity = Decimal('100.00')  # Placeholder
                    
                    # Calculate settlement
                    calc_result = settlement_service.calculate_settlement(
                        customer_id=customer.id,
                        config=config,
                        usage_quantity=usage_quantity,
                        period_start=period_start,
                        period_end=period_end
                    )
                    
                    # Create settlement record
                    settlement = settlement_service.create_settlement_record(
                        session=session,
                        calculation_result=calc_result,
                        config_id=config.id,
                        generated_by=getattr(req, 'current_user', {}).get('user_id')
                    )
                    
                    session.add(settlement)
                    generated += 1
                    
                except Exception as e:
                    logger.error(f"Failed to generate settlement for customer {customer.id}: {str(e)}")
                    failed += 1
                    errors.append({
                        'customer_id': customer.id,
                        'error': str(e)
                    })
            
            session.commit()
            
            return json({
                'success': True,
                'data': {
                    'generation_id': generation_id,
                    'total_customers': len(customers),
                    'generated': generated,
                    'failed': failed,
                    'errors': errors,
                    'status': 'completed' if failed == 0 else 'partial'
                },
                'message': f'Settlement generation completed: {generated} succeeded, {failed} failed'
            })
            
        finally:
            session.close()
            
    except SettlementCalculationError as e:
        logger.error(f"Settlement calculation error: {str(e)}")
        return json({
            'success': False,
            'error': 'Calculation error',
            'message': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to generate settlements: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@settlement_bp.route('', methods=['GET'])
async def list_settlements(req: request.Request):
    """
    List settlements with filtering and pagination
    
    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - customer_id: Filter by customer ID
    - status: Filter by status (pending, approved, paid)
    - period_start: Filter by period start date
    - period_end: Filter by period end date
    
    Returns:
    {
        "success": true,
        "data": {
            "settlements": [...],
            "total": 100,
            "page": 1,
            "page_size": 20,
            "total_pages": 5
        }
    }
    """
    try:
        # Parse query parameters
        page = max(1, int(req.args.get('page', 1)))
        page_size = min(100, max(1, int(req.args.get('page_size', 20))))
        customer_id = req.args.get('customer_id', '')
        status = req.args.get('status', '')
        period_start = req.args.get('period_start', '')
        period_end = req.args.get('period_end', '')
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Build query
            query = session.query(SettlementRecord)
            
            # Apply filters
            if customer_id:
                query = query.filter(SettlementRecord.customer_id == int(customer_id))
            if status:
                query = query.filter(SettlementRecord.status == status)
            
            # Get total count
            total = query.count()
            
            # Get paginated results
            settlements = query.order_by(
                SettlementRecord.created_at.desc()
            ).offset(offset).limit(page_size).all()
            
            # Convert to response format
            settlement_list = []
            for s in settlements:
                settlement_list.append({
                    'id': s.id,
                    'record_id': s.record_id,
                    'customer_id': s.customer_id,
                    'config_id': s.config_id,
                    'period_start': s.period_start.isoformat() if s.period_start else None,
                    'period_end': s.period_end.isoformat() if s.period_end else None,
                    'usage_quantity': float(s.usage_quantity) if s.usage_quantity else None,
                    'unit': s.unit,
                    'price_model': s.price_model,
                    'unit_price': float(s.unit_price) if s.unit_price else None,
                    'total_amount': float(s.total_amount) if s.total_amount else None,
                    'currency': s.currency,
                    'status': s.status,
                    'created_at': s.created_at.isoformat() if s.created_at else None,
                    'updated_at': s.updated_at.isoformat() if s.updated_at else None
                })
            
            # Calculate total pages
            total_pages = (total + page_size - 1) // page_size
            
            return json({
                'success': True,
                'data': {
                    'settlements': settlement_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages
                },
                'message': f'Retrieved {len(settlement_list)} settlements'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to list settlements: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@settlement_bp.route('/<record_id:int>', methods=['GET'])
async def get_settlement(req: request.Request, record_id: int):
    """
    Get settlement details by ID
    
    Returns:
    {
        "success": true,
        "data": { ...settlement details... }
    }
    """
    try:
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            settlement = session.query(SettlementRecord).filter(
                SettlementRecord.id == record_id
            ).first()
            
            if not settlement:
                raise NotFound("Settlement not found")
            
            return json({
                'success': True,
                'data': {
                    'id': settlement.id,
                    'record_id': settlement.record_id,
                    'customer_id': settlement.customer_id,
                    'config_id': settlement.config_id,
                    'period_start': settlement.period_start.isoformat() if settlement.period_start else None,
                    'period_end': settlement.period_end.isoformat() if settlement.period_end else None,
                    'usage_quantity': float(settlement.usage_quantity) if settlement.usage_quantity else None,
                    'unit': settlement.unit,
                    'price_model': settlement.price_model,
                    'unit_price': float(settlement.unit_price) if settlement.unit_price else None,
                    'total_amount': float(settlement.total_amount) if settlement.total_amount else None,
                    'currency': settlement.currency,
                    'status': settlement.status,
                    'remarks': settlement.remarks,
                    'calculation_breakdown': settlement.calculation_breakdown,
                    'created_at': settlement.created_at.isoformat() if settlement.created_at else None,
                    'updated_at': settlement.updated_at.isoformat() if settlement.updated_at else None
                }
            })
            
        finally:
            session.close()
            
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to get settlement: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
