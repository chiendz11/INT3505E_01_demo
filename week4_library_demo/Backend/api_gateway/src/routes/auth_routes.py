from flask import Blueprint, request, jsonify, current_app, Response, g
from ..auth.decorators import admin_required, token_required
import requests

auth_bp = Blueprint('auth_bp', __name__)

def _proxy_request(service_url, path, new_data=None):
    """Hàm chung để proxy request."""
    try:
        downstream_url = f"{service_url}/{path}"
        
        # Thêm header user nếu đã được xác thực
        headers = {key: value for (key, value) in request.headers if key != 'Host'}
        if hasattr(g, 'user'):
            headers['X-User-ID'] = g.user.get('user_id')
            headers['X-User-Role'] = g.user.get('role')

        resp = requests.request(
            method=request.method,
            url=downstream_url,
            headers=headers,
            # Sửa lại để truyền đúng data/json
            data=request.get_data() if new_data is None else None,
            json=new_data,
            params=request.args,
            timeout=5,
            allow_redirects=False # Quan trọng: Không để gateway tự động theo redirect
        )
        
        # Xử lý trường hợp redirect (như trong luồng OAuth)
        if resp.is_redirect:
            # LỖI CŨ:
            # return Response(status=resp.status_code, headers={'Location': resp.headers['Location']})
            
            # ✅ SỬA LỖI (Chuẩn Dev):
            # Phải proxy *tất cả* header (bao gồm 'Location' và 'Set-Cookie')
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            headers = [
                (name, value) for (name, value) in resp.raw.headers.items() 
                if name.lower() not in excluded_headers
            ]
            
            # Trả về Response với đầy đủ header
            return Response(status=resp.status_code, headers=headers)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response_data = resp.content
        return Response(response_data, resp.status_code, headers)

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Service is unavailable"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request to service timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================================
# RESTful Authentication Endpoints (Email/Password)
# ==================================

@auth_bp.route('/users', methods=['POST'])
def register_user():
    """Tạo một tài nguyên 'user' mới. Endpoint: POST /api/users"""
    url = current_app.config['AUTH_SERVICE_URL']
    return _proxy_request(url, 'auth/users')

@auth_bp.route('/auth/login', methods=['POST'])
def create_token():
    """Tạo một tài nguyên 'token' mới (Đăng nhập). Endpoint: POST /api/auth/tokens"""
    url = current_app.config['AUTH_SERVICE_URL']
    return _proxy_request(url, 'auth/login')

# --- [V2] ĐĂNG NHẬP (BỔ SUNG) ---
@auth_bp.route('/v2/auth/login', methods=['POST'])
def create_token_v2():
    """
    [V2] Tạo một tài nguyên 'token' mới (Đăng nhập) với response đầy đủ.
    Endpoint: POST /api/v2/auth/tokens
    Proxy to: auth_service/auth/v2/login
    """
    url = current_app.config['AUTH_SERVICE_URL']
    # Hàm proxy sẽ chuyển tiếp request đến endpoint v2 của auth_service
    # (Endpoint này bạn đã tạo ở auth_service trong bước trước)
    return _proxy_request(url, 'auth/v2/login')
# --- [V3] BỔ SUNG ---
@auth_bp.route('/v3/auth/login', methods=['POST'])
def create_token_v3():
    """[V3] Endpoint: POST /api/v3/auth/tokens"""
    url = current_app.config['AUTH_SERVICE_URL']
    return _proxy_request(url, 'auth/v3/login') # -> auth_service/auth/v3/login

# --- [V4] BỔ SUNG ---
@auth_bp.route('/v4/auth/login', methods=['POST'])
def create_token_v4():
    """[V4] Endpoint: POST /api/v4/auth/tokens"""
    url = current_app.config['AUTH_SERVICE_URL']
    return _proxy_request(url, 'auth/v4/login') # -> auth_service/auth/v4/login

# --- [V5] BỔ SUNG ---
@auth_bp.route('/v5/auth/login', methods=['POST'])
def create_token_v5():
    """[V5] Endpoint: POST /api/v5/auth/tokens"""
    url = current_app.config['AUTH_SERVICE_URL']
    return _proxy_request(url, 'auth/v5/login') # -> auth_service/auth/v5/login

@auth_bp.route('/auth/refresh-token', methods=['PUT'])
def refresh_token():
    """Cập nhật/Làm mới một 'access token'. Endpoint: PUT /api/auth/tokens"""
    url = current_app.config['AUTH_SERVICE_URL']
    return _proxy_request(url, 'auth/refresh-token')

@auth_bp.route('/auth/logout', methods=['DELETE'])
@token_required
def delete_token():
    """Xóa một tài nguyên 'token' (Đăng xuất). Endpoint: DELETE /api/auth/tokens"""
    url = current_app.config['AUTH_SERVICE_URL']
    return _proxy_request(url, 'auth/logout')

# ==================================
# Google OAuth 2.0 Endpoints
# ==================================

@auth_bp.route('/auth/google/login', methods=['GET'])
def google_login():
    """
    Bắt đầu luồng đăng nhập với Google. 
    Endpoint: GET /api/auth/google/login
    (Proxy to auth_service/auth/google/login)
    """
    url = current_app.config['AUTH_SERVICE_URL']
    # Hàm proxy sẽ tự động xử lý và trả về redirect response cho trình duyệt
    return _proxy_request(url, 'auth/google/login')

@auth_bp.route('/auth/google/callback', methods=['GET'])
def google_callback():
    """
    Xử lý callback từ Google sau khi người dùng đăng nhập.
    Endpoint: GET /api/auth/google/callback
    (Proxy to auth_service/auth/google/callback)
    """
    url = current_app.config['AUTH_SERVICE_URL']
    # Hàm proxy sẽ chuyển tiếp 'code' và 'state' từ Google đến auth_service
    # và trả về kết quả (tokens hoặc redirect) cho client
    return _proxy_request(url, 'auth/google/callback')

@auth_bp.route('/users/nplus1', methods=['GET'])
@token_required
@admin_required
def debug_users_nplus1():
    """
    ❌ Gây ra N+1 Query Problem.
    Endpoint FE gọi: GET /api/users/nplus1
    Proxy to: auth_service/auth/users/nplus1
    """
    url = current_app.config['AUTH_SERVICE_URL']
    return _proxy_request(url, 'auth/users/nplus1')


@auth_bp.route('/users/eager', methods=['GET'])
@token_required
@admin_required
def debug_users_eager():
    """
    ✅ Giải pháp: Eager Loading.
    Endpoint FE gọi: GET /api/users/eager
    Proxy to: auth_service/auth/users/eager
    """
    url = current_app.config['AUTH_SERVICE_URL']
    return _proxy_request(url, 'auth/users/eager')


@auth_bp.route('/users/batch', methods=['GET'])
@token_required
@admin_required
def debug_users_batch():
    """
    ✅ Giải pháp: Batch Loading.
    Endpoint FE gọi: GET /api/users/batch
    Proxy to: auth_service/auth/users/batch
    """
    url = current_app.config['AUTH_SERVICE_URL']
    return _proxy_request(url, 'auth/users/batch')

# ==================================