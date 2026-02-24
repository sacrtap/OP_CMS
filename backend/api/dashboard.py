# OP_CMS Dashboard API
# Story 4.1: Management Dashboard

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest
from typing import Optional
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from backend.models.database_models import SettlementRecord, Customer, PriceConfig
from backend.dao.database_dao import DatabaseSessionFactory

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', url_prefix='/dashboard')


@dashboard_bp.route('/metrics', methods=['GET'])
async def get_dashboard_metrics(req: request.Request):
    """
    Get core dashboard metrics
    
    Query Parameters:
    - dimension: time dimension (day/week/month) - default: month
    
    Returns:
    {
        "success": true,
        "data": {
            "total_revenue": 1000000,
            "total_customers": 1320,
            "active_customers": 1200,
            "pending_payment": 200000,
            "overdue_payment": 50000,
            "collection_rate": 0.85,
            "customer_churn_rate": 0.05,
            "month_over_month_growth": 0.15,
            "year_over_year_growth": 0.25
        }
    }
    """
    try:
        dimension = req.args.get('dimension', 'month')
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Calculate metrics
            # Total revenue (sum of all paid settlements)
            total_revenue_query = session.query(SettlementRecord).filter(
                SettlementRecord.status == 'paid'
            )
            total_revenue = sum([s.total_amount for s in total_revenue_query.all()]) if total_revenue_query.count() > 0 else Decimal('0')
            
            # Total customers
            total_customers = session.query(Customer).count()
            
            # Active customers (with active settlements)
            active_customer_ids = session.query(SettlementRecord.customer_id).filter(
                SettlementRecord.status.in_(['pending', 'approved', 'paid'])
            ).distinct()
            active_customers = session.query(Customer).filter(Customer.id.in_(active_customer_ids)).count()
            
            # Pending payment (approved but not paid)
            pending_payment_query = session.query(SettlementRecord).filter(
                SettlementRecord.status.in_(['pending', 'approved'])
            )
            pending_payment = sum([s.total_amount for s in pending_payment_query.all()]) if pending_payment_query.count() > 0 else Decimal('0')
            
            # Overdue payment (pending for > 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            overdue_query = session.query(SettlementRecord).filter(
                SettlementRecord.status.in_(['pending', 'approved']),
                SettlementRecord.created_at < thirty_days_ago
            )
            overdue_payment = sum([s.total_amount for s in overdue_query.all()]) if overdue_query.count() > 0 else Decimal('0')
            
            # Collection rate (paid / (paid + pending))
            paid_amount = sum([s.total_amount for s in session.query(SettlementRecord).filter(SettlementRecord.status == 'paid').all()]) if session.query(SettlementRecord).filter(SettlementRecord.status == 'paid').count() > 0 else Decimal('0')
            total_amount = paid_amount + pending_payment
            collection_rate = float(paid_amount / total_amount) if total_amount > 0 else 0.0
            
            # Customer churn rate (simplified - customers with no activity in 90 days)
            ninety_days_ago = datetime.utcnow() - timedelta(days=90)
            active_customer_ids_recent = session.query(SettlementRecord.customer_id).filter(
                SettlementRecord.created_at >= ninety_days_ago
            ).distinct()
            active_customers_recent = session.query(Customer).filter(Customer.id.in_(active_customer_ids_recent)).count()
            customer_churn_rate = 1.0 - (active_customers_recent / total_customers) if total_customers > 0 else 0.0
            
            # Month-over-month growth (simplified)
            current_month_revenue = sum([s.total_amount for s in session.query(SettlementRecord).filter(
                SettlementRecord.status == 'paid',
                SettlementRecord.created_at >= datetime.utcnow().replace(day=1)
            ).all()])
            
            last_month_start = (datetime.utcnow().replace(day=1) - timedelta(days=1)).replace(day=1)
            last_month_end = datetime.utcnow().replace(day=1) - timedelta(days=1)
            last_month_revenue = sum([s.total_amount for s in session.query(SettlementRecord).filter(
                SettlementRecord.status == 'paid',
                SettlementRecord.created_at >= last_month_start,
                SettlementRecord.created_at <= last_month_end
            ).all()])
            
            month_over_month_growth = float((current_month_revenue - last_month_revenue) / last_month_revenue) if last_month_revenue > 0 else 0.0
            
            return json({
                'success': True,
                'data': {
                    'total_revenue': float(total_revenue),
                    'total_customers': total_customers,
                    'active_customers': active_customers,
                    'pending_payment': float(pending_payment),
                    'overdue_payment': float(overdue_payment),
                    'collection_rate': collection_rate,
                    'customer_churn_rate': customer_churn_rate,
                    'month_over_month_growth': month_over_month_growth,
                    'last_updated': datetime.utcnow().isoformat()
                },
                'message': 'Dashboard metrics retrieved successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to get dashboard metrics: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@dashboard_bp.route('/trends', methods=['GET'])
async def get_dashboard_trends(req: request.Request):
    """
    Get trend data for charts
    
    Query Parameters:
    - dimension: time dimension (day/week/month) - default: month
    - range: number of periods to show - default: 6
    
    Returns:
    {
        "success": true,
        "data": {
            "revenue_trend": [...],
            "payment_trend": [...],
            "customer_growth": [...]
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
            # Generate date ranges based on dimension
            now = datetime.utcnow()
            date_ranges = []
            
            for i in range(range_count):
                if dimension == 'day':
                    start_date = now - timedelta(days=i)
                    end_date = start_date
                elif dimension == 'week':
                    start_date = now - timedelta(weeks=i)
                    end_date = start_date + timedelta(days=6)
                else:  # month
                    start_date = now.replace(day=1) - timedelta(days=i*30)
                    end_date = start_date + timedelta(days=30)
                
                date_ranges.append({
                    'start': start_date,
                    'end': end_date,
                    'label': start_date.strftime('%Y-%m') if dimension == 'month' else start_date.strftime('%Y-%m-%d')
                })
            
            # Get revenue trend
            revenue_trend = []
            for date_range in reversed(date_ranges):  # Reverse to get chronological order
                revenue = session.query(SettlementRecord).filter(
                    SettlementRecord.status == 'paid',
                    SettlementRecord.created_at >= date_range['start'],
                    SettlementRecord.created_at <= date_range['end']
                ).all()
                
                total = sum([s.total_amount for s in revenue]) if revenue else Decimal('0')
                revenue_trend.append({
                    'date': date_range['label'],
                    'value': float(total)
                })
            
            # Get payment trend
            payment_trend = []
            for date_range in reversed(date_ranges):
                payments = session.query(SettlementRecord).filter(
                    SettlementRecord.status.in_(['pending', 'approved', 'paid']),
                    SettlementRecord.created_at >= date_range['start'],
                    SettlementRecord.created_at <= date_range['end']
                ).all()
                
                total = sum([s.total_amount for s in payments]) if payments else Decimal('0')
                payment_trend.append({
                    'date': date_range['label'],
                    'value': float(total)
                })
            
            # Get customer growth
            customer_growth = []
            for date_range in reversed(date_ranges):
                customers = session.query(Customer).filter(
                    Customer.created_at >= date_range['start'],
                    Customer.created_at <= date_range['end']
                ).count()
                
                customer_growth.append({
                    'date': date_range['label'],
                    'value': customers
                })
            
            return json({
                'success': True,
                'data': {
                    'revenue_trend': revenue_trend,
                    'payment_trend': payment_trend,
                    'customer_growth': customer_growth,
                    'dimension': dimension,
                    'range': range_count
                },
                'message': 'Dashboard trends retrieved successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to get dashboard trends: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@dashboard_bp.route('/customer-stats', methods=['GET'])
async def get_customer_stats(req: request.Request):
    """
    Get customer statistics for charts
    
    Returns:
    {
        "success": true,
        "data": {
            "industry_distribution": [...],
            "region_distribution": [...],
            "level_distribution": [...]
        }
    }
    """
    try:
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Get industry distribution
            all_customers = session.query(Customer).all()
            
            industry_stats = {}
            region_stats = {}
            level_stats = {}
            
            for customer in all_customers:
                # Industry
                industry = customer.industry or '未分类'
                industry_stats[industry] = industry_stats.get(industry, 0) + 1
                
                # Region
                region = customer.province or '未分类'
                region_stats[region] = region_stats.get(region, 0) + 1
                
                # Level
                level = customer.level or 'standard'
                level_stats[level] = level_stats.get(level, 0) + 1
            
            return json({
                'success': True,
                'data': {
                    'industry_distribution': [
                        {'name': k, 'value': v} for k, v in industry_stats.items()
                    ],
                    'region_distribution': [
                        {'name': k, 'value': v} for k, v in region_stats.items()
                    ],
                    'level_distribution': [
                        {'name': k, 'value': v} for k, v in level_stats.items()
                    ],
                    'total_customers': len(all_customers)
                },
                'message': 'Customer statistics retrieved successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to get customer stats: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
