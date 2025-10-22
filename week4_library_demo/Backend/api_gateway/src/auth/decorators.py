from functools import wraps
from flask import request, jsonify, current_app, g
import requests

def _validate_token(token_header):
    """Hàm nội bộ gọi đến Auth Service để xác thực token."""
    if not token_header or not token_header.startswith('Bearer '):
        return None, "Missing or invalid Authorization header"

    auth_service_url = current_app.config['AUTH_SERVICE_URL']
    validate_url = f"{auth_service_url}/auth/validate"
    
    try:
        response = requests.post(
            validate_url,
            headers={'Authorization': token_header},
        )
        
        if response.status_code == 200:
            user_data = response.json().get('user')
            return user_data, None # {"user_id": "...", "role": "admin"}
        else:
            return None, response.json().get('error', 'Invalid token')

    except requests.exceptions.RequestException as e:
        print(f"Error validating token: {e}")
        return None, "Authentication service is unavailable"

def token_required(f):
    """
    Decorator: Yêu cầu token hợp lệ (cho cả 'user' và 'admin').
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        user_data, error = _validate_token(token_header)
        
        if error:
            return jsonify({"error": error}), 401
            
        # Lưu thông tin user vào 'g' để các hàm sau có thể dùng
        g.user = user_data
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator: Yêu cầu token hợp lệ VÀ role='admin'.
    PHẢI được dùng *SAU* @token_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # @token_required đã chạy trước, nên g.user phải tồn tại
        if not hasattr(g, 'user') or g.user.get('role') != 'ADMIN':
            return jsonify({"error": "Admin access required"}), 403 # 403 Forbidden
        
        return f(*args, **kwargs)
    return decorated_function