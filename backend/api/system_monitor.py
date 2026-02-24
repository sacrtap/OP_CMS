# OP_CMS System Monitor API
# Story 7.2: System Running Status Monitoring

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest
from typing import Optional
import logging
import psutil
import os
from datetime import datetime, timedelta

from backend.utils.jwt import require_auth, require_role

logger = logging.getLogger(__name__)

system_monitor_bp = Blueprint('system_monitor', url_prefix='/system')


@system_monitor_bp.route('/status', methods=['GET'])
@require_auth
@require_role('admin')
async def get_system_status(req: request.Request):
    """
    Get system status
    
    Returns:
    {
        "success": true,
        "data": {
            "cpu_usage": 45.5,
            "memory_usage": 67.8,
            "disk_usage": 52.3,
            "services": {
                "database": "running",
                "redis": "running",
                "application": "running"
            },
            "uptime": 86400
        }
    }
    """
    try:
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=0.1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        # Get system uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = (datetime.utcnow() - boot_time).total_seconds()
        
        # Check service status (simplified)
        services = {
            'database': check_service_status('database'),
            'redis': check_service_status('redis'),
            'application': 'running'  # We're running, so application is up
        }
        
        return json({
            'success': True,
            'data': {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'disk_usage': disk_usage,
                'services': services,
                'uptime': int(uptime),
                'boot_time': boot_time.isoformat(),
                'timestamp': datetime.utcnow().isoformat()
            },
            'message': 'System status retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@system_monitor_bp.route('/resources', methods=['GET'])
@require_auth
@require_role('admin')
async def get_system_resources(req: request.Request):
    """
    Get detailed system resources information
    
    Query Parameters:
    - history: Include historical data (default: false)
    - hours: Number of hours of history (default: 24)
    
    Returns:
    {
        "success": true,
        "data": {
            "cpu": {...},
            "memory": {...},
            "disk": {...},
            "network": {...}
        }
    }
    """
    try:
        include_history = req.args.get('history', 'false').lower() == 'true'
        history_hours = int(req.args.get('hours', 24))
        
        # Get current CPU info
        cpu_info = {
            'usage_percent': psutil.cpu_percent(interval=0.1),
            'cores': psutil.cpu_count(),
            'cores_physical': psutil.cpu_count(logical=False),
            'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0
        }
        
        # Get current memory info
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'total_gb': round(memory.total / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2)
        }
        
        # Get disk info
        disk = psutil.disk_usage('/')
        disk_info = {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent,
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2)
        }
        
        # Get network info
        net_io = psutil.net_io_counters()
        network_info = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'bytes_sent_gb': round(net_io.bytes_sent / (1024**3), 2),
            'bytes_recv_gb': round(net_io.bytes_recv / (1024**3), 2)
        }
        
        # Generate historical data (mock for now)
        history = None
        if include_history:
            history = generate_mock_history(history_hours)
        
        return json({
            'success': True,
            'data': {
                'cpu': cpu_info,
                'memory': memory_info,
                'disk': disk_info,
                'network': network_info,
                'history': history,
                'timestamp': datetime.utcnow().isoformat()
            },
            'message': 'System resources retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to get system resources: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@system_monitor_bp.route('/logs', methods=['GET'])
@require_auth
@require_role('admin')
async def get_system_logs(req: request.Request):
    """
    Get system logs
    
    Query Parameters:
    - level: Log level (INFO, WARNING, ERROR)
    - from: Start date (ISO format)
    - to: End date (ISO format)
    - limit: Maximum number of logs (default: 100)
    - offset: Offset for pagination (default: 0)
    
    Returns:
    {
        "success": true,
        "data": {
            "logs": [...],
            "total": 1000
        }
    }
    """
    try:
        # Parse query parameters
        level = req.args.get('level', '')
        from_date = req.args.get('from', '')
        to_date = req.args.get('to', '')
        limit = min(int(req.args.get('limit', 100)), 1000)
        offset = int(req.args.get('offset', 0))
        
        # Mock log data (in production, read from actual log files)
        mock_logs = generate_mock_logs(level, from_date, to_date, limit + offset)
        
        # Apply pagination
        paginated_logs = mock_logs[offset:offset + limit]
        
        return json({
            'success': True,
            'data': {
                'logs': paginated_logs,
                'total': len(mock_logs),
                'limit': limit,
                'offset': offset,
                'filters': {
                    'level': level,
                    'from': from_date,
                    'to': to_date
                }
            },
            'message': 'System logs retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to get system logs: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@system_monitor_bp.route('/errors', methods=['GET'])
@require_auth
@require_role('admin')
async def get_system_errors(req: request.Request):
    """
    Get system errors
    
    Query Parameters:
    - from: Start date (ISO format)
    - to: End date (ISO format)
    - limit: Maximum number of errors (default: 100)
    
    Returns:
    {
        "success": true,
        "data": {
            "errors": [...],
            "total": 50
        }
    }
    """
    try:
        # Parse query parameters
        from_date = req.args.get('from', '')
        to_date = req.args.get('to', '')
        limit = min(int(req.args.get('limit', 100)), 1000)
        
        # Mock error data (in production, read from actual error logs)
        mock_errors = generate_mock_errors(from_date, to_date, limit)
        
        return json({
            'success': True,
            'data': {
                'errors': mock_errors,
                'total': len(mock_errors),
                'limit': limit,
                'filters': {
                    'from': from_date,
                    'to': to_date
                }
            },
            'message': 'System errors retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to get system errors: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


def check_service_status(service_name: str) -> str:
    """
    Check if a service is running
    
    Args:
        service_name: Name of the service
        
    Returns:
        'running', 'stopped', or 'unknown'
    """
    # Simplified check - in production, use actual service checks
    try:
        if service_name == 'database':
            # Check if MySQL/MariaDB is running
            for proc in psutil.process_iter(['name']):
                if 'mysql' in proc.info['name'].lower() or 'mariadb' in proc.info['name'].lower():
                    return 'running'
            return 'unknown'  # Can't determine without direct connection
            
        elif service_name == 'redis':
            # Check if Redis is running
            for proc in psutil.process_iter(['name']):
                if 'redis' in proc.info['name'].lower():
                    return 'running'
            return 'unknown'
            
        else:
            return 'unknown'
            
    except:
        return 'unknown'


def generate_mock_logs(level: str = '', from_date: str = '', to_date: str = '', limit: int = 100) -> list:
    """Generate mock log entries"""
    import random
    
    levels = ['INFO', 'WARNING', 'ERROR']
    if level:
        levels = [level]
    
    messages = [
        'User login successful',
        'Data export completed',
        'Customer record updated',
        'Settlement calculation started',
        'Import validation completed',
        'Cache cleared',
        'Configuration updated',
        'Batch job completed',
        'Email notification sent',
        'Report generated'
    ]
    
    logs = []
    now = datetime.utcnow()
    
    for i in range(limit):
        timestamp = now - timedelta(hours=random.randint(0, 72), minutes=random.randint(0, 59))
        
        # Filter by date range
        if from_date and timestamp < datetime.fromisoformat(from_date):
            continue
        if to_date and timestamp > datetime.fromisoformat(to_date):
            continue
        
        log_level = random.choice(levels)
        logs.append({
            'id': i + 1,
            'timestamp': timestamp.isoformat(),
            'level': log_level,
            'message': random.choice(messages),
            'source': 'application',
            'user_id': random.randint(1, 10) if random.random() > 0.5 else None
        })
    
    # Sort by timestamp (newest first)
    logs.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return logs


def generate_mock_errors(from_date: str = '', to_date: str = '', limit: int = 100) -> list:
    """Generate mock error entries"""
    import random
    
    error_types = [
        'ValidationError',
        'DatabaseError',
        'ImportError',
        'ExportError',
        'AuthenticationError',
        'PermissionDenied',
        'TimeoutError'
    ]
    
    errors = []
    now = datetime.utcnow()
    
    for i in range(limit):
        timestamp = now - timedelta(hours=random.randint(0, 168), minutes=random.randint(0, 59))
        
        # Filter by date range
        if from_date and timestamp < datetime.fromisoformat(from_date):
            continue
        if to_date and timestamp > datetime.fromisoformat(to_date):
            continue
        
        errors.append({
            'id': i + 1,
            'timestamp': timestamp.isoformat(),
            'type': random.choice(error_types),
            'message': f'Error occurred in module {random.choice(["auth", "import", "export", "settlement", "customer"])}',
            'stack_trace': f'File "app.py", line {random.randint(100, 500)}, in function\n  raise {random.choice(error_types)}("Mock error")',
            'user_id': random.randint(1, 10) if random.random() > 0.5 else None,
            'resolved': random.choice([True, False])
        })
    
    # Sort by timestamp (newest first)
    errors.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return errors


def generate_mock_history(hours: int = 24) -> dict:
    """Generate mock historical data"""
    import random
    
    now = datetime.utcnow()
    history = {
        'cpu': [],
        'memory': [],
        'disk': []
    }
    
    for i in range(hours):
        timestamp = now - timedelta(hours=hours - i)
        
        history['cpu'].append({
            'timestamp': timestamp.isoformat(),
            'value': random.uniform(20, 80)
        })
        
        history['memory'].append({
            'timestamp': timestamp.isoformat(),
            'value': random.uniform(50, 80)
        })
        
        history['disk'].append({
            'timestamp': timestamp.isoformat(),
            'value': random.uniform(40, 60)
        })
    
    return history
