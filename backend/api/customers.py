# OP_CMS Customer API Endpoints
# RESTful API for Customer Management

"""
Customer Management API - Story 1.1

Endpoints:
- GET /api/v1/customers - List customers with pagination
- GET /api/v1/customers/{customer_id} - Get customer details
- POST /api/v1/customers - Create new customer
- PUT /api/v1/customers/{customer_id} - Update customer
- DELETE /api/v1/customers/{customer_id} - Delete customer
- GET /api/v1/customers/check-duplicate - Check for duplicate customers
"""

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest
from typing import Optional
import logging
import uuid

from backend.models.database_models import (
    Customer, CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
)
from backend.dao.database_dao import DatabaseSessionFactory

logger = logging.getLogger(__name__)

customer_bp = Blueprint('customer', url_prefix='/api/v1/customers')


@customer_bp.route('', methods=['GET'])
async def list_customers(req: request.Request):
    """
    List customers with pagination and filtering
    
    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - search: Search term (company_name or contact_name)
    - status: Filter by status (active, inactive, potential)
    - province: Filter by province
    - level: Filter by customer level (vip, standard, economy)
    
    Returns:
    - Customer list with pagination metadata
    """
    try:
        # Parse query parameters
        page = max(1, int(req.args.get('page', 1)))
        page_size = min(100, max(1, int(req.args.get('page_size', 20))))
        search = req.args.get('search', '')
        status = req.args.get('status', '')
        province = req.args.get('province', '')
        level = req.args.get('level', '')
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Build query with filters
            query = session.query(Customer)
            
            if search:
                search_term = f'%{search}%'
                query = query.filter(
                    (Customer.company_name.like(search_term)) |
                    (Customer.contact_name.like(search_term))
                )
            
            if status:
                query = query.filter(Customer.status == status)
            
            if province:
                query = query.filter(Customer.province == province)
            
            if level:
                query = query.filter(Customer.level == level)
            
            # Get total count
            total = query.count()
            
            # Get paginated results
            customers = query.order_by(Customer.created_at.desc()).offset(offset).limit(page_size).all()
            
            # Calculate total pages
            total_pages = (total + page_size - 1) // page_size
            
            # Convert to response format
            customer_responses = [
                CustomerResponse(
                    id=c.id,
                    customer_id=c.customer_id,
                    company_name=c.company_name,
                    contact_name=c.contact_name,
                    contact_phone=c.contact_phone,
                    credit_code=c.credit_code,
                    customer_type=c.customer_type,
                    province=c.province,
                    city=c.city,
                    address=c.address,
                    email=c.email,
                    website=c.website,
                    industry=c.industry,
                    erp_system=c.erp_system,
                    erp_customer_code=c.erp_customer_code,
                    status=c.status,
                    level=c.level,
                    source=c.source,
                    remarks=c.remarks,
                    created_at=c.created_at,
                    updated_at=c.updated_at
                ) for c in customers
            ]
            
            response_data = CustomerListResponse(
                customers=customer_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
            return json({
                'success': True,
                'data': response_data.model_dump(),
                'message': f'Retrieved {len(customer_responses)} customers'
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
        logger.error(f"Failed to list customers: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@customer_bp.route('', methods=['POST'])
async def create_customer(req: request.Request):
    """
    Create a new customer
    
    Request Body:
    - company_name (required): Company name
    - contact_name (required): Contact person name
    - contact_phone (required): Contact phone
    - credit_code (optional): Unified social credit code
    - customer_type (optional): enterprise or individual
    - province (optional): Province
    - city (optional): City
    - address (optional): Full address
    - email (optional): Email address
    - website (optional): Company website
    - industry (optional): Industry category
    - erp_system (optional): ERP system name
    - erp_customer_code (optional): ERP customer code
    - status (optional): active, inactive, potential
    - level (optional): vip, standard, economy
    - source (optional): direct, referral, marketing
    - remarks (optional): Additional remarks
    
    Returns:
    - Created customer data
    """
    try:
        # Parse and validate request body
        try:
            customer_data = CustomerCreate(**req.json)
        except ValueError as e:
            return json({
                'success': False,
                'error': 'Validation error',
                'message': str(e)
            }, status=400)
        
        # Check for duplicates
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Check duplicate by company_name
            existing_by_name = session.query(Customer).filter(
                Customer.company_name == customer_data.company_name
            ).first()
            
            if existing_by_name:
                return json({
                    'success': False,
                    'error': 'Duplicate customer',
                    'message': f'Customer with company name "{customer_data.company_name}" already exists'
                }, status=409)
            
            # Check duplicate by credit_code if provided
            if customer_data.credit_code:
                existing_by_code = session.query(Customer).filter(
                    Customer.credit_code == customer_data.credit_code
                ).first()
                
                if existing_by_code:
                    return json({
                        'success': False,
                        'error': 'Duplicate customer',
                        'message': f'Customer with credit code "{customer_data.credit_code}" already exists'
                    }, status=409)
            
            # Create new customer
            new_customer = Customer(
                customer_id=str(uuid.uuid4()),
                company_name=customer_data.company_name,
                contact_name=customer_data.contact_name,
                contact_phone=customer_data.contact_phone,
                credit_code=customer_data.credit_code,
                customer_type=customer_data.customer_type,
                province=customer_data.province,
                city=customer_data.city,
                address=customer_data.address,
                email=customer_data.email,
                website=customer_data.website,
                industry=customer_data.industry,
                erp_system=customer_data.erp_system,
                erp_customer_code=customer_data.erp_customer_code,
                status=customer_data.status,
                level=customer_data.level,
                source=customer_data.source,
                remarks=customer_data.remarks
            )
            
            session.add(new_customer)
            session.commit()
            session.refresh(new_customer)
            
            # Return created customer
            response_data = CustomerResponse(
                id=new_customer.id,
                customer_id=new_customer.customer_id,
                company_name=new_customer.company_name,
                contact_name=new_customer.contact_name,
                contact_phone=new_customer.contact_phone,
                credit_code=new_customer.credit_code,
                customer_type=new_customer.customer_type,
                province=new_customer.province,
                city=new_customer.city,
                address=new_customer.address,
                email=new_customer.email,
                website=new_customer.website,
                industry=new_customer.industry,
                erp_system=new_customer.erp_system,
                erp_customer_code=new_customer.erp_customer_code,
                status=new_customer.status,
                level=new_customer.level,
                source=new_customer.source,
                remarks=new_customer.remarks,
                created_at=new_customer.created_at,
                updated_at=new_customer.updated_at
            )
            
            return json({
                'success': True,
                'data': response_data.model_dump(),
                'message': 'Customer created successfully'
            }, status=201)
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to create customer: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@customer_bp.route('/<customer_id:string>', methods=['GET'])
async def get_customer(req: request.Request, customer_id: str):
    """
    Get customer details by customer_id (UUID)
    
    Path Parameters:
    - customer_id: Customer UUID
    
    Returns:
    - Customer details
    """
    try:
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            customer = session.query(Customer).filter(
                Customer.customer_id == customer_id
            ).first()
            
            if not customer:
                return json({
                    'success': False,
                    'error': 'Not found',
                    'message': f'Customer with id "{customer_id}" not found'
                }, status=404)
            
            response_data = CustomerResponse(
                id=customer.id,
                customer_id=customer.customer_id,
                company_name=customer.company_name,
                contact_name=customer.contact_name,
                contact_phone=customer.contact_phone,
                credit_code=customer.credit_code,
                customer_type=customer.customer_type,
                province=customer.province,
                city=customer.city,
                address=customer.address,
                email=customer.email,
                website=customer.website,
                industry=customer.industry,
                erp_system=customer.erp_system,
                erp_customer_code=customer.erp_customer_code,
                status=customer.status,
                level=customer.level,
                source=customer.source,
                remarks=customer.remarks,
                created_at=customer.created_at,
                updated_at=customer.updated_at
            )
            
            return json({
                'success': True,
                'data': response_data.model_dump(),
                'message': 'Customer retrieved successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to get customer: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@customer_bp.route('/<customer_id:string>', methods=['PUT'])
async def update_customer(req: request.Request, customer_id: str):
    """
    Update customer information
    
    Path Parameters:
    - customer_id: Customer UUID
    
    Request Body:
    - All fields are optional (partial update supported)
    
    Returns:
    - Updated customer data
    """
    try:
        # Parse and validate request body
        try:
            update_data = CustomerUpdate(**req.json)
        except ValueError as e:
            return json({
                'success': False,
                'error': 'Validation error',
                'message': str(e)
            }, status=400)
        
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            customer = session.query(Customer).filter(
                Customer.customer_id == customer_id
            ).first()
            
            if not customer:
                return json({
                    'success': False,
                    'error': 'Not found',
                    'message': f'Customer with id "{customer_id}" not found'
                }, status=404)
            
            # Check for duplicate company_name if updating
            if update_data.company_name and update_data.company_name != customer.company_name:
                existing = session.query(Customer).filter(
                    Customer.company_name == update_data.company_name,
                    Customer.customer_id != customer_id
                ).first()
                
                if existing:
                    return json({
                        'success': False,
                        'error': 'Duplicate customer',
                        'message': f'Company name "{update_data.company_name}" already exists'
                    }, status=409)
            
            # Check for duplicate credit_code if updating
            if update_data.credit_code and update_data.credit_code != customer.credit_code:
                existing = session.query(Customer).filter(
                    Customer.credit_code == update_data.credit_code,
                    Customer.customer_id != customer_id
                ).first()
                
                if existing:
                    return json({
                        'success': False,
                        'error': 'Duplicate customer',
                        'message': f'Credit code "{update_data.credit_code}" already exists'
                    }, status=409)
            
            # Update fields (only update non-None values)
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                if value is not None:
                    setattr(customer, field, value)
            
            session.commit()
            session.refresh(customer)
            
            response_data = CustomerResponse(
                id=customer.id,
                customer_id=customer.customer_id,
                company_name=customer.company_name,
                contact_name=customer.contact_name,
                contact_phone=customer.contact_phone,
                credit_code=customer.credit_code,
                customer_type=customer.customer_type,
                province=customer.province,
                city=customer.city,
                address=customer.address,
                email=customer.email,
                website=customer.website,
                industry=customer.industry,
                erp_system=customer.erp_system,
                erp_customer_code=customer.erp_customer_code,
                status=customer.status,
                level=customer.level,
                source=customer.source,
                remarks=customer.remarks,
                created_at=customer.created_at,
                updated_at=customer.updated_at
            )
            
            return json({
                'success': True,
                'data': response_data.model_dump(),
                'message': 'Customer updated successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to update customer: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@customer_bp.route('/check-duplicate', methods=['GET'])
async def check_duplicate(req: request.Request):
    """
    Check if a customer already exists by company_name or credit_code
    
    Query Parameters:
    - company_name (optional): Company name to check
    - credit_code (optional): Credit code to check
    
    Returns:
    - Duplicate check result
    """
    try:
        company_name = req.args.get('company_name', '')
        credit_code = req.args.get('credit_code', '')
        
        if not company_name and not credit_code:
            return json({
                'success': False,
                'error': 'Bad request',
                'message': 'Either company_name or credit_code must be provided'
            }, status=400)
        
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            is_duplicate = False
            duplicate_field = None
            duplicate_value = None
            
            if company_name:
                existing = session.query(Customer).filter(
                    Customer.company_name == company_name
                ).first()
                
                if existing:
                    is_duplicate = True
                    duplicate_field = 'company_name'
                    duplicate_value = company_name
            
            if not is_duplicate and credit_code:
                existing = session.query(Customer).filter(
                    Customer.credit_code == credit_code
                ).first()
                
                if existing:
                    is_duplicate = True
                    duplicate_field = 'credit_code'
                    duplicate_value = credit_code
            
            return json({
                'success': True,
                'data': {
                    'is_duplicate': is_duplicate,
                    'duplicate_field': duplicate_field,
                    'duplicate_value': duplicate_value
                },
                'message': 'Duplicate check completed'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to check duplicate: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@customer_bp.route('/<customer_id:string>', methods=['DELETE'])
async def delete_customer(req: request.Request, customer_id: str):
    """
    Delete customer by customer_id (UUID)
    
    Path Parameters:
    - customer_id: Customer UUID
    
    Returns:
    - Deletion confirmation
    """
    try:
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            customer = session.query(Customer).filter(
                Customer.customer_id == customer_id
            ).first()
            
            if not customer:
                return json({
                    'success': False,
                    'error': 'Not found',
                    'message': f'Customer with id "{customer_id}" not found'
                }, status=404)
            
            # Delete customer (cascade will handle related records)
            session.delete(customer)
            session.commit()
            
            return json({
                'success': True,
                'data': None,
                'message': f'Customer "{customer.company_name}" deleted successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to delete customer: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
