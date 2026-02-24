# OP_CMS Customer Import/Export API
# Story 6.2: Import/Export Enhancement

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest
from typing import Optional, List, Dict
import logging
import base64
import io
from datetime import datetime

from backend.models.database_models import Customer
from backend.dao.database_dao import DatabaseSessionFactory
from backend.services.data_validation_service import DataValidationService

logger = logging.getLogger(__name__)

customer_import_export_bp = Blueprint('customer_import_export', url_prefix='/customers')


@customer_import_export_bp.route('/import', methods=['POST'])
async def import_customers(req: request.Request):
    """
    Import customers from Excel/CSV file
    
    Request Body:
    {
        "file": "base64_encoded_file",
        "file_name": "customers.xlsx",
        "import_mode": "skip_duplicates",  // skip_duplicates, update_duplicates, create_all
        "validate_only": false
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "total_rows": 100,
            "imported": 95,
            "skipped": 5,
            "updated": 0,
            "errors": [...]
        }
    }
    """
    try:
        data = req.json
        
        # Validate required fields
        file_data = data.get('file')
        file_name = data.get('file_name', 'import.xlsx')
        import_mode = data.get('import_mode', 'skip_duplicates')
        validate_only = data.get('validate_only', False)
        
        if not file_data:
            return json({
                'success': False,
                'error': 'Missing required fields',
                'message': 'file is required'
            }, status=400)
        
        if import_mode not in ['skip_duplicates', 'update_duplicates', 'create_all']:
            return json({
                'success': False,
                'error': 'Invalid import mode',
                'message': f'Invalid import mode: {import_mode}. Valid modes: skip_duplicates, update_duplicates, create_all'
            }, status=400)
        
        # Decode file
        try:
            file_content = base64.b64decode(file_data)
        except Exception as e:
            return json({
                'success': False,
                'error': 'Invalid file',
                'message': f'Failed to decode file: {str(e)}'
            }, status=400)
        
        # Parse Excel/CSV file
        rows = parse_file(file_content, file_name)
        
        if not rows:
            return json({
                'success': False,
                'error': 'Empty file',
                'message': 'No data found in file'
            }, status=400)
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Initialize validation service
            validation_service = DataValidationService()
            
            # Validate all rows
            validation_report = validation_service.validate_batch(rows, session)
            
            # If validate_only, return validation results
            if validate_only:
                return json({
                    'success': True,
                    'data': {
                        'validation_only': True,
                        **validation_report
                    },
                    'message': 'Validation completed'
                })
            
            # Import data based on mode
            import_result = execute_import(
                session=session,
                rows=rows,
                validation_results=validation_report['results'],
                import_mode=import_mode
            )
            
            return json({
                'success': True,
                'data': import_result,
                'message': f'Import completed: {import_result["imported"]} imported, {import_result["skipped"]} skipped, {import_result["updated"]} updated'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to import customers: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@customer_import_export_bp.route('/export', methods=['POST'])
async def export_customers(req: request.Request):
    """
    Export customers to Excel/CSV file
    
    Request Body:
    {
        "format": "excel",  // excel, csv
        "filters": {
            "status": "active",
            "level": "vip",
            ...
        },
        "fields": ["company_name", "contact_name", ...],
        "template_id": null  // optional
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "file_content": "base64_encoded",
            "file_name": "customers_20260320.xlsx",
            "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "total_records": 1000
        }
    }
    """
    try:
        data = req.json
        
        # Parse parameters
        export_format = data.get('format', 'excel')
        filters = data.get('filters', {})
        fields = data.get('fields', None)  # None means all fields
        template_id = data.get('template_id')
        
        # If template_id provided, load template
        if template_id:
            # TODO: Load template from database
            pass
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Build query
            query = session.query(Customer)
            
            # Apply filters
            if filters.get('status'):
                query = query.filter(Customer.status == filters['status'])
            
            if filters.get('level'):
                query = query.filter(Customer.level == filters['level'])
            
            if filters.get('customer_type'):
                query = query.filter(Customer.customer_type == filters['customer_type'])
            
            # Get customers
            customers = query.all()
            
            # Convert to dict
            customers_data = []
            for customer in customers:
                customer_dict = customer.to_dict()
                
                # Filter fields if specified
                if fields:
                    customer_dict = {k: v for k, v in customer_dict.items() if k in fields}
                
                customers_data.append(customer_dict)
            
            # Generate file
            file_content, file_name = generate_export_file(
                customers_data=customers_data,
                export_format=export_format,
                fields=fields
            )
            
            # Encode to base64
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            return json({
                'success': True,
                'data': {
                    'file_content': encoded_content,
                    'file_name': file_name,
                    'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if export_format == 'excel' else 'text/csv',
                    'total_records': len(customers_data)
                },
                'message': f'Export completed: {len(customers_data)} records'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to export customers: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


def parse_file(file_content: bytes, file_name: str) -> List[Dict[str, any]]:
    """
    Parse Excel/CSV file and return list of rows
    
    Args:
        file_content: File content as bytes
        file_name: File name with extension
        
    Returns:
        List of row dictionaries
    """
    try:
        import pandas as pd
        
        # Create BytesIO object
        file_io = io.BytesIO(file_content)
        
        # Parse based on file extension
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_io)
        else:  # Excel
            df = pd.read_excel(file_io, engine='openpyxl')
        
        # Convert to list of dicts
        rows = df.to_dict('records')
        
        # Clean data (remove None, strip strings)
        cleaned_rows = []
        for row in rows:
            cleaned_row = {}
            for key, value in row.items():
                if pd.isna(value):
                    cleaned_row[key] = None
                elif isinstance(value, str):
                    cleaned_row[key] = value.strip()
                else:
                    cleaned_row[key] = value
            cleaned_rows.append(cleaned_row)
        
        return cleaned_rows
        
    except Exception as e:
        logger.error(f"Failed to parse file: {str(e)}")
        raise BadRequest(f"Failed to parse file: {str(e)}")


def execute_import(
    session,
    rows: List[Dict[str, any]],
    validation_results: List[Dict[str, any]],
    import_mode: str
) -> Dict[str, any]:
    """
    Execute customer import
    
    Args:
        session: Database session
        rows: List of row data
        validation_results: List of validation results
        import_mode: Import mode (skip_duplicates, update_duplicates, create_all)
        
    Returns:
        Import result summary
    """
    imported = 0
    skipped = 0
    updated = 0
    errors = []
    
    validation_service = DataValidationService()
    
    for idx, (row_data, validation) in enumerate(zip(rows, validation_results), 1):
        try:
            # Check validation
            if not validation['is_valid']:
                skipped += 1
                errors.append({
                    'row': idx,
                    'errors': validation['errors'],
                    'action': 'skipped'
                })
                continue
            
            # Check duplicates
            duplicates = validation_service.check_duplicates(row_data, session)
            
            if duplicates and import_mode == 'skip_duplicates':
                skipped += 1
                errors.append({
                    'row': idx,
                    'duplicates': duplicates,
                    'action': 'skipped'
                })
                continue
            
            if duplicates and import_mode == 'update_duplicates':
                # Update existing customer
                customer_id = duplicates[0]['customer_id']
                customer = session.query(Customer).filter(Customer.id == customer_id).first()
                
                if customer:
                    # Update fields
                    for key, value in row_data.items():
                        if hasattr(customer, key) and value is not None:
                            setattr(customer, key, value)
                    
                    session.commit()
                    updated += 1
                    continue
            
            # Create new customer (create_all or no duplicates)
            import uuid
            new_customer = Customer(
                customer_id=str(uuid.uuid4()),
                company_name=row_data.get('company_name'),
                contact_name=row_data.get('contact_name'),
                contact_phone=row_data.get('contact_phone'),
                credit_code=row_data.get('credit_code'),
                customer_type=row_data.get('customer_type', 'enterprise'),
                province=row_data.get('province'),
                city=row_data.get('city'),
                address=row_data.get('address'),
                email=row_data.get('email'),
                website=row_data.get('website'),
                industry=row_data.get('industry'),
                erp_system=row_data.get('erp_system'),
                erp_customer_code=row_data.get('erp_customer_code'),
                status=row_data.get('status', 'active'),
                level=row_data.get('level', 'standard'),
                source=row_data.get('source', 'direct'),
                remarks=row_data.get('remarks')
            )
            
            session.add(new_customer)
            session.commit()
            imported += 1
            
        except Exception as e:
            session.rollback()
            skipped += 1
            errors.append({
                'row': idx,
                'error': str(e),
                'action': 'failed'
            })
    
    return {
        'total_rows': len(rows),
        'imported': imported,
        'skipped': skipped,
        'updated': updated,
        'errors': errors[:100],  # Limit errors to first 100
        'import_mode': import_mode
    }


def generate_export_file(
    customers_data: List[Dict[str, any]],
    export_format: str,
    fields: Optional[List[str]] = None
) -> tuple:
    """
    Generate export file
    
    Args:
        customers_data: List of customer dictionaries
        export_format: File format (excel, csv)
        fields: Fields to export (None means all)
        
    Returns:
        Tuple of (file_content, file_name)
    """
    try:
        import pandas as pd
        
        # Create DataFrame
        df = pd.DataFrame(customers_data)
        
        # Select columns if specified
        if fields:
            available_columns = [col for col in fields if col in df.columns]
            df = df[available_columns]
        
        # Generate file
        output = io.BytesIO()
        
        if export_format == 'csv':
            df.to_csv(output, index=False, encoding='utf-8-sig')
            file_name = f"customers_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        else:  # Excel
            df.to_excel(output, index=False, engine='openpyxl')
            file_name = f"customers_{datetime.utcnow().strftime('%Y%m%d')}.xlsx"
        
        output.seek(0)
        return output.getvalue(), file_name
        
    except Exception as e:
        logger.error(f"Failed to generate export file: {str(e)}")
        raise Exception(f"Failed to generate export file: {str(e)}")
