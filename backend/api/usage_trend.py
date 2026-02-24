# OP_CMS Usage Trend API
# Story 4.3: Customer Usage Trend Analysis

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest
from typing import Optional
import logging
from datetime import datetime, timedelta
from decimal import Decimal
import statistics

from backend.models.database_models import SettlementRecord, Customer
from backend.dao.database_dao import DatabaseSessionFactory

logger = logging.getLogger(__name__)

usage_trend_bp = Blueprint('usage_trend', url_prefix='/customers')


@usage_trend_bp.route('/<customer_id:int>/usage-trend', methods=['GET'])
async def get_customer_usage_trend(req: request.Request, customer_id: int):
    """
    Get customer usage trend analysis
    
    Query Parameters:
    - dimension: time dimension (month/quarter/year) - default: month
    - range: number of periods to show - default: 6
    
    Returns:
    {
        "success": true,
        "data": {
            "customer_id": 1,
            "company_name": "Test Company",
            "trend": [...],
            "anomalies": [...],
            "dimension": "month",
            "range": 6
        }
    }
    """
    try:
        dimension = req.args.get('dimension', 'month')
        range_count = int(req.args.get('range', 6))
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Get customer
            customer = session.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise NotFound("Customer not found")
            
            # Get settlements for this customer
            settlements = session.query(SettlementRecord).filter(
                SettlementRecord.customer_id == customer_id,
                SettlementRecord.status == 'paid'
            ).all()
            
            if not settlements:
                return json({
                    'success': True,
                    'data': {
                        'customer_id': customer_id,
                        'company_name': customer.company_name,
                        'trend': [],
                        'anomalies': [],
                        'dimension': dimension,
                        'range': range_count,
                        'message': 'No usage data available'
                    }
                })
            
            # Generate date ranges based on dimension
            now = datetime.utcnow()
            date_ranges = []
            
            for i in range(range_count):
                if dimension == 'month':
                    start_date = now - timedelta(days=i*30)
                    label = start_date.strftime('%Y-%m')
                elif dimension == 'quarter':
                    start_date = now - timedelta(days=i*90)
                    label = f"Q{((start_date.month - 1) // 3) + 1} {start_date.year}"
                else:  # year
                    start_date = now - timedelta(days=i*365)
                    label = str(start_date.year)
                
                date_ranges.append({
                    'start': start_date,
                    'label': label
                })
            
            # Calculate usage trend
            trend = []
            for date_range in reversed(date_ranges):  # Reverse to get chronological order
                # Filter settlements in this period
                period_settlements = [
                    s for s in settlements
                    if s.created_at >= date_range['start']
                ]
                
                # Calculate total usage and amount
                total_usage = sum([float(s.usage_quantity) for s in period_settlements]) if period_settlements else 0.0
                total_amount = sum([float(s.total_amount) for s in period_settlements]) if period_settlements else 0.0
                
                trend.append({
                    'date': date_range['label'],
                    'usage': total_usage,
                    'amount': total_amount,
                    'count': len(period_settlements)
                })
            
            # Detect anomalies
            anomalies = detect_usage_anomalies(trend)
            
            return json({
                'success': True,
                'data': {
                    'customer_id': customer_id,
                    'company_name': customer.company_name,
                    'contact_name': customer.contact_name,
                    'trend': trend,
                    'anomalies': anomalies,
                    'dimension': dimension,
                    'range': range_count,
                    'total_usage': sum([t['usage'] for t in trend]),
                    'total_amount': sum([t['amount'] for t in trend]),
                    'average_monthly_usage': sum([t['usage'] for t in trend]) / len(trend) if trend else 0,
                    'last_updated': datetime.utcnow().isoformat()
                },
                'message': 'Customer usage trend retrieved successfully'
            })
            
        finally:
            session.close()
            
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to get usage trend: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


def detect_usage_anomalies(trend: list) -> list:
    """
    Detect anomalies in usage trend
    
    Methods:
    - Month-over-month change > 50%
    - Z-score > 2 (2 standard deviations)
    
    Args:
        trend: List of trend data points
    
    Returns:
        List of anomalies
    """
    anomalies = []
    
    if len(trend) < 2:
        return anomalies
    
    # Extract usage values
    usage_values = [t['usage'] for t in trend]
    
    # Calculate statistics
    mean_usage = statistics.mean(usage_values) if usage_values else 0
    std_usage = statistics.stdev(usage_values) if len(usage_values) > 1 else 0
    
    for i, data in enumerate(trend):
        anomaly_types = []
        
        # Check month-over-month change
        if i > 0:
            prev_usage = trend[i-1]['usage']
            if prev_usage > 0:
                change_rate = (data['usage'] - prev_usage) / prev_usage
                
                if change_rate > 0.5:  # 50% increase
                    anomaly_types.append({
                        'type': 'spike',
                        'severity': 'high' if change_rate > 1.0 else 'medium',
                        'description': f"用量激增 {change_rate*100:.1f}%",
                        'change_rate': change_rate
                    })
                elif change_rate < -0.5:  # 50% decrease
                    anomaly_types.append({
                        'type': 'drop',
                        'severity': 'high' if change_rate < -0.8 else 'medium',
                        'description': f"用量骤降 {abs(change_rate)*100:.1f}%",
                        'change_rate': change_rate
                    })
        
        # Check Z-score
        if std_usage > 0 and data['usage'] > 0:
            z_score = (data['usage'] - mean_usage) / std_usage
            
            if abs(z_score) > 2:
                anomaly_type = 'high' if z_score > 0 else 'low'
                anomaly_types.append({
                    'type': 'statistical_outlier',
                    'severity': 'high' if abs(z_score) > 3 else 'medium',
                    'description': f"统计异常 ({anomaly_type}): Z-score={z_score:.2f}",
                    'z_score': z_score
                })
        
        # Add anomalies for this data point
        if anomaly_types:
            anomalies.append({
                'date': data['date'],
                'usage': data['usage'],
                'anomaly_types': anomaly_types,
                'primary_anomaly': anomaly_types[0]  # Most significant anomaly
            })
    
    return anomalies
