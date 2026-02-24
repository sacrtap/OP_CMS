# OP_CMS Settlement Approval API
# Story 3.2: Settlement Approval Workflow

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest
from typing import List
import logging
from datetime import datetime

from backend.models.database_models import SettlementRecord
from backend.dao.database_dao import DatabaseSessionFactory

logger = logging.getLogger(__name__)

# Use the existing settlement_bp from settlements.py
# These routes will be added to the existing blueprint


def register_approval_routes(bp: Blueprint):
    """Register approval workflow routes to the settlement blueprint"""
    
    @bp.route('/<record_id:int>/approve', methods=['PUT'])
    async def approve_settlement(req: request.Request, record_id: int):
        """
        Approve a settlement
        
        Request Body:
        {
            "approved_by": 1,  // User ID
            "approval_remarks": "Approved"
        }
        """
        try:
            data = req.json
            
            # Validate required fields
            if not data.get('approved_by'):
                return json({
                    'success': False,
                    'error': 'Missing required fields',
                    'message': 'approved_by is required'
                }, status=400)
            
            # Get database session
            session_factory = DatabaseSessionFactory()
            session = session_factory.get_session()
            
            try:
                # Find settlement
                settlement = session.query(SettlementRecord).filter(
                    SettlementRecord.id == record_id
                ).first()
                
                if not settlement:
                    raise NotFound("Settlement not found")
                
                # Check if already approved
                if settlement.status == 'approved':
                    return json({
                        'success': False,
                        'error': 'Already approved',
                        'message': 'This settlement has already been approved'
                    }, status=400)
                
                # Update settlement
                settlement.status = 'approved'
                settlement.approved_at = datetime.utcnow()
                settlement.approved_by = data['approved_by']
                settlement.approval_remarks = data.get('approval_remarks', '')
                
                session.commit()
                
                return json({
                    'success': True,
                    'data': {
                        'id': settlement.id,
                        'status': 'approved',
                        'approved_at': settlement.approved_at.isoformat() if settlement.approved_at else None,
                        'approved_by': settlement.approved_by
                    },
                    'message': 'Settlement approved successfully'
                })
                
            finally:
                session.close()
                
        except NotFound as e:
            raise
        except Exception as e:
            logger.error(f"Failed to approve settlement: {str(e)}")
            return json({
                'success': False,
                'error': 'Internal server error',
                'message': str(e)
            }, status=500)
    
    
    @bp.route('/<record_id:int>/reject', methods=['PUT'])
    async def reject_settlement(req: request.Request, record_id: int):
        """
        Reject a settlement
        
        Request Body:
        {
            "rejected_by": 1,  // User ID
            "rejection_reason": "Incorrect usage data"
        }
        """
        try:
            data = req.json
            
            # Validate required fields
            if not data.get('rejected_by'):
                return json({
                    'success': False,
                    'error': 'Missing required fields',
                    'message': 'rejected_by is required'
                }, status=400)
            
            if not data.get('rejection_reason'):
                return json({
                    'success': False,
                    'error': 'Missing required fields',
                    'message': 'rejection_reason is required'
                }, status=400)
            
            # Get database session
            session_factory = DatabaseSessionFactory()
            session = session_factory.get_session()
            
            try:
                # Find settlement
                settlement = session.query(SettlementRecord).filter(
                    SettlementRecord.id == record_id
                ).first()
                
                if not settlement:
                    raise NotFound("Settlement not found")
                
                # Check if already rejected
                if settlement.status == 'rejected':
                    return json({
                        'success': False,
                        'error': 'Already rejected',
                        'message': 'This settlement has already been rejected'
                    }, status=400)
                
                # Update settlement
                settlement.status = 'rejected'
                settlement.rejected_at = datetime.utcnow()
                settlement.rejected_by = data['rejected_by']
                settlement.rejection_reason = data['rejection_reason']
                
                session.commit()
                
                return json({
                    'success': True,
                    'data': {
                        'id': settlement.id,
                        'status': 'rejected',
                        'rejected_at': settlement.rejected_at.isoformat() if settlement.rejected_at else None,
                        'rejected_by': settlement.rejected_by,
                        'rejection_reason': settlement.rejection_reason
                    },
                    'message': 'Settlement rejected successfully'
                })
                
            finally:
                session.close()
                
        except NotFound as e:
            raise
        except Exception as e:
            logger.error(f"Failed to reject settlement: {str(e)}")
            return json({
                'success': False,
                'error': 'Internal server error',
                'message': str(e)
            }, status=500)
    
    
    @bp.route('/bulk-approve', methods=['POST'])
    async def bulk_approve_settlements(req: request.Request):
        """
        Bulk approve multiple settlements
        
        Request Body:
        {
            "settlement_ids": [1, 2, 3],
            "approved_by": 1
        }
        
        Returns:
        {
            "success": true,
            "data": {
                "total": 3,
                "approved": 3,
                "failed": 0,
                "errors": []
            }
        }
        """
        try:
            data = req.json
            
            # Validate required fields
            if not data.get('settlement_ids') or not data.get('approved_by'):
                return json({
                    'success': False,
                    'error': 'Missing required fields',
                    'message': 'settlement_ids and approved_by are required'
                }, status=400)
            
            settlement_ids: List[int] = data['settlement_ids']
            approved_by: int = data['approved_by']
            
            # Get database session
            session_factory = DatabaseSessionFactory()
            session = session_factory.get_session()
            
            try:
                approved = 0
                failed = 0
                errors = []
                
                for settlement_id in settlement_ids:
                    try:
                        # Find settlement
                        settlement = session.query(SettlementRecord).filter(
                            SettlementRecord.id == settlement_id
                        ).first()
                        
                        if not settlement:
                            failed += 1
                            errors.append({
                                'settlement_id': settlement_id,
                                'error': 'Settlement not found'
                            })
                            continue
                        
                        # Skip if already approved
                        if settlement.status == 'approved':
                            failed += 1
                            errors.append({
                                'settlement_id': settlement_id,
                                'error': 'Already approved'
                            })
                            continue
                        
                        # Update settlement
                        settlement.status = 'approved'
                        settlement.approved_at = datetime.utcnow()
                        settlement.approved_by = approved_by
                        
                        approved += 1
                        
                    except Exception as e:
                        failed += 1
                        errors.append({
                            'settlement_id': settlement_id,
                            'error': str(e)
                        })
                
                session.commit()
                
                return json({
                    'success': True,
                    'data': {
                        'total': len(settlement_ids),
                        'approved': approved,
                        'failed': failed,
                        'errors': errors
                    },
                    'message': f'Bulk approval completed: {approved} approved, {failed} failed'
                })
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Failed to bulk approve settlements: {str(e)}")
            return json({
                'success': False,
                'error': 'Internal server error',
                'message': str(e)
            }, status=500)
