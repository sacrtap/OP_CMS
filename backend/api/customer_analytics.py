# OP_CMS Customer Segmentation API
# Story 4.2: Customer Segmentation and Risk Warning

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest
from typing import Optional
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from backend.models.database_models import SettlementRecord, Customer
from backend.dao.database_dao import DatabaseSessionFactory

logger = logging.getLogger(__name__)

customer_analytics_bp = Blueprint('customer_analytics', url_prefix='/customers')


@customer_analytics_bp.route('/segmentation', methods=['GET'])
async def get_customer_segmentation(req: request.Request):
    """
    Get customer segmentation based on RFM model
    
    Query Parameters:
    - method: segmentation method (rfm, revenue) - default: rfm
    
    Returns:
    {
        "success": true,
        "data": {
            "segments": [
                {
                    "name": "VIP",
                    "count": 50,
                    "percentage": 0.15,
                    "customers": [...]
                },
                ...
            ],
            "total_customers": 1320
        }
    }
    """
    try:
        method = req.args.get('method', 'rfm')
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Get all customers with settlement data
            customers = session.query(Customer).all()
            
            segments = {
                'vip': {'name': 'VIP 客户', 'customers': [], 'count': 0},
                'loyal': {'name': '忠诚客户', 'customers': [], 'count': 0},
                'general': {'name': '一般客户', 'customers': [], 'count': 0},
                'at_risk': {'name': '风险客户', 'customers': [], 'count': 0},
                'lost': {'name': '流失客户', 'customers': [], 'count': 0}
            }
            
            for customer in customers:
                # Calculate RFM scores
                rfm_data = calculate_rfm_score(customer, session)
                
                # Determine segment based on RFM scores
                if rfm_data['r_score'] >= 3 and rfm_data['f_score'] >= 3 and rfm_data['m_score'] >= 3:
                    segment = 'vip'
                elif rfm_data['r_score'] >= 3 and rfm_data['f_score'] >= 2:
                    segment = 'loyal'
                elif rfm_data['r_score'] <= 2 and rfm_data['f_score'] >= 3:
                    segment = 'at_risk'
                elif rfm_data['r_score'] <= 1 and rfm_data['f_score'] <= 2:
                    segment = 'lost'
                else:
                    segment = 'general'
                
                # Add customer to segment
                customer_data = {
                    'id': customer.id,
                    'company_name': customer.company_name,
                    'contact_name': customer.contact_name,
                    'level': customer.level,
                    'rfm_scores': rfm_data,
                    'total_revenue': float(rfm_data['total_revenue']),
                    'last_purchase': rfm_data['last_purchase'].isoformat() if rfm_data['last_purchase'] else None
                }
                
                segments[segment]['customers'].append(customer_data)
                segments[segment]['count'] += 1
            
            # Calculate percentages
            total_customers = len(customers)
            for segment_key in segments:
                segments[segment_key]['percentage'] = segments[segment_key]['count'] / total_customers if total_customers > 0 else 0
            
            return json({
                'success': True,
                'data': {
                    'segments': list(segments.values()),
                    'total_customers': total_customers,
                    'segmentation_method': method,
                    'last_updated': datetime.utcnow().isoformat()
                },
                'message': 'Customer segmentation retrieved successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to get customer segmentation: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@customer_analytics_bp.route('/risks', methods=['GET'])
async def get_customer_risks(req: request.Request):
    """
    Get customer risk warning list
    
    Query Parameters:
    - risk_type: risk type (overdue, churn, decline) - default: all
    - risk_level: risk level (high, medium, low) - default: all
    
    Returns:
    {
        "success": true,
        "data": {
            "risks": [
                {
                    "customer_id": 1,
                    "company_name": "Test Company",
                    "risk_type": "overdue",
                    "risk_level": "high",
                    "risk_score": 85,
                    "risk_factors": [...],
                    "overdue_amount": 50000,
                    "overdue_days": 45
                },
                ...
            ],
            "total_risks": 10,
            "high_risk_count": 3,
            "medium_risk_count": 5,
            "low_risk_count": 2
        }
    }
    """
    try:
        risk_type = req.args.get('risk_type', 'all')
        risk_level = req.args.get('risk_level', 'all')
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Get all customers
            customers = session.query(Customer).all()
            risks = []
            
            for customer in customers:
                # Calculate risk factors
                risk_factors = []
                risk_score = 0
                
                # Check overdue risk
                overdue_data = check_overdue_risk(customer, session)
                if overdue_data['has_overdue']:
                    risk_factors.append({
                        'type': 'overdue',
                        'severity': 'high' if overdue_data['overdue_days'] > 60 else 'medium',
                        'description': f"逾期金额 ¥{overdue_data['overdue_amount']}, 逾期 {overdue_data['overdue_days']} 天"
                    })
                    risk_score += 40 if overdue_data['overdue_days'] > 60 else 20
                
                # Check churn risk
                churn_data = check_churn_risk(customer, session)
                if churn_data['is_churn_risk']:
                    risk_factors.append({
                        'type': 'churn',
                        'severity': 'high' if churn_data['inactive_days'] > 120 else 'medium',
                        'description': f"无活动 {churn_data['inactive_days']} 天"
                    })
                    risk_score += 30 if churn_data['inactive_days'] > 120 else 15
                
                # Check revenue decline risk
                decline_data = check_revenue_decline(customer, session)
                if decline_data['has_decline']:
                    risk_factors.append({
                        'type': 'decline',
                        'severity': 'high' if decline_data['decline_rate'] > 0.7 else 'medium',
                        'description': f"收入下降 {decline_data['decline_rate']*100:.1f}%"
                    })
                    risk_score += 30 if decline_data['decline_rate'] > 0.7 else 15
                
                # Skip customers with no risks
                if not risk_factors:
                    continue
                
                # Determine risk level
                if risk_score >= 60:
                    risk_level_str = 'high'
                elif risk_score >= 30:
                    risk_level_str = 'medium'
                else:
                    risk_level_str = 'low'
                
                # Filter by risk type
                if risk_type != 'all':
                    if not any(f['type'] == risk_type for f in risk_factors):
                        continue
                
                # Filter by risk level
                if risk_level != 'all' and risk_level_str != risk_level:
                    continue
                
                # Add to risks list
                risk_data = {
                    'customer_id': customer.id,
                    'company_name': customer.company_name,
                    'contact_name': customer.contact_name,
                    'level': customer.level,
                    'risk_type': risk_factors[0]['type'],  # Primary risk type
                    'risk_level': risk_level_str,
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'overdue_amount': overdue_data['overdue_amount'],
                    'overdue_days': overdue_data['overdue_days'],
                    'inactive_days': churn_data['inactive_days'],
                    'decline_rate': decline_data['decline_rate']
                }
                
                risks.append(risk_data)
            
            # Sort by risk score (descending)
            risks.sort(key=lambda x: x['risk_score'], reverse=True)
            
            # Count by risk level
            high_risk_count = sum(1 for r in risks if r['risk_level'] == 'high')
            medium_risk_count = sum(1 for r in risks if r['risk_level'] == 'medium')
            low_risk_count = sum(1 for r in risks if r['risk_level'] == 'low')
            
            return json({
                'success': True,
                'data': {
                    'risks': risks,
                    'total_risks': len(risks),
                    'high_risk_count': high_risk_count,
                    'medium_risk_count': medium_risk_count,
                    'low_risk_count': low_risk_count,
                    'filters': {
                        'risk_type': risk_type,
                        'risk_level': risk_level
                    },
                    'last_updated': datetime.utcnow().isoformat()
                },
                'message': 'Customer risks retrieved successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to get customer risks: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


def calculate_rfm_score(customer: Customer, session) -> dict:
    """Calculate RFM scores for a customer"""
    now = datetime.utcnow()
    
    # Get customer settlements
    settlements = session.query(SettlementRecord).filter(
        SettlementRecord.customer_id == customer.id
    ).all()
    
    if not settlements:
        return {
            'r_score': 1,
            'f_score': 1,
            'm_score': 1,
            'total_revenue': Decimal('0'),
            'last_purchase': None
        }
    
    # Recency: Days since last purchase
    last_purchase = max([s.created_at for s in settlements])
    recency_days = (now - last_purchase).days
    r_score = 5 if recency_days <= 30 else (4 if recency_days <= 60 else (3 if recency_days <= 90 else (2 if recency_days <= 180 else 1)))
    
    # Frequency: Number of purchases
    frequency = len(settlements)
    f_score = 5 if frequency >= 10 else (4 if frequency >= 5 else (3 if frequency >= 3 else (2 if frequency >= 2 else 1)))
    
    # Monetary: Total revenue
    total_revenue = sum([s.total_amount for s in settlements])
    m_score = 5 if total_revenue >= 100000 else (4 if total_revenue >= 50000 else (3 if total_revenue >= 10000 else (2 if total_revenue >= 1000 else 1)))
    
    return {
        'r_score': r_score,
        'f_score': f_score,
        'm_score': m_score,
        'total_revenue': total_revenue,
        'last_purchase': last_purchase
    }


def check_overdue_risk(customer: Customer, session) -> dict:
    """Check if customer has overdue payments"""
    # Get pending/approved settlements
    pending_settlements = session.query(SettlementRecord).filter(
        SettlementRecord.customer_id == customer.id,
        SettlementRecord.status.in_(['pending', 'approved'])
    ).all()
    
    if not pending_settlements:
        return {
            'has_overdue': False,
            'overdue_amount': 0,
            'overdue_days': 0
        }
    
    # Check for overdue (> 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    overdue_settlements = [s for s in pending_settlements if s.created_at < thirty_days_ago]
    
    if not overdue_settlements:
        return {
            'has_overdue': False,
            'overdue_amount': 0,
            'overdue_days': 0
        }
    
    total_overdue = sum([s.total_amount for s in overdue_settlements])
    max_overdue_days = max([(datetime.utcnow() - s.created_at).days for s in overdue_settlements])
    
    return {
        'has_overdue': True,
        'overdue_amount': float(total_overdue),
        'overdue_days': max_overdue_days
    }


def check_churn_risk(customer: Customer, session) -> dict:
    """Check if customer is at risk of churning"""
    # Get last settlement
    last_settlement = session.query(SettlementRecord).filter(
        SettlementRecord.customer_id == customer.id
    ).order_by(SettlementRecord.created_at.desc()).first()
    
    if not last_settlement:
        return {
            'is_churn_risk': True,
            'inactive_days': 999
        }
    
    inactive_days = (datetime.utcnow() - last_settlement.created_at).days
    
    # Churn risk if no activity in 90 days
    is_churn_risk = inactive_days > 90
    
    return {
        'is_churn_risk': is_churn_risk,
        'inactive_days': inactive_days
    }


def check_revenue_decline(customer: Customer, session) -> dict:
    """Check if customer revenue is declining"""
    now = datetime.utcnow()
    
    # Get current month revenue
    current_month_start = now.replace(day=1)
    current_settlements = session.query(SettlementRecord).filter(
        SettlementRecord.customer_id == customer.id,
        SettlementRecord.status == 'paid',
        SettlementRecord.created_at >= current_month_start
    ).all()
    current_revenue = sum([s.total_amount for s in current_settlements]) if current_settlements else Decimal('0')
    
    # Get last month revenue
    last_month_end = current_month_start - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    last_settlements = session.query(SettlementRecord).filter(
        SettlementRecord.customer_id == customer.id,
        SettlementRecord.status == 'paid',
        SettlementRecord.created_at >= last_month_start,
        SettlementRecord.created_at <= last_month_end
    ).all()
    last_revenue = sum([s.total_amount for s in last_settlements]) if last_settlements else Decimal('0')
    
    if last_revenue == 0:
        return {
            'has_decline': False,
            'decline_rate': 0
        }
    
    decline_rate = float((last_revenue - current_revenue) / last_revenue)
    has_decline = decline_rate > 0.5  # 50% decline
    
    return {
        'has_decline': has_decline,
        'decline_rate': decline_rate
    }
