import json
from flask import Blueprint, request, jsonify, current_app, make_response, redirect, session
from ..services.auth_service import AuthService
from ..services.oauth_service import oauth, OAuthService
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not all([email, username, password]):
        return jsonify({"error": "Email, username, và password là bắt buộc"}), 400

    service = AuthService()
    user, error = service.register_user(email, username, password)
    if error:
        return jsonify({"error": error}), 409 # 409 Conflict
        
    return jsonify({"message": "Đăng ký thành công", "user_id": user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    login_identifier = data.get('login')
    password = data.get('password')

    if not all([login_identifier, password]):
        return jsonify({"error": "Login và password là bắt buộc"}), 400

    service = AuthService()
    # [FIX] Nhận 4 giá trị trả về, bao gồm cả object 'user'
    user, access_token, refresh_token_data, error = service.login_user(login_identifier, password)

    if error:
        return jsonify({"error": error}), 401

    # [FIX] Tạo một dictionary an toàn chứa thông tin user để gửi về client
    user_profile = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role
    }
    
    # [FIX] Thêm object 'user' vào trong body của response JSON
    response = make_response(jsonify({
        "access_token": access_token,
        "user": user_profile
    }))
    
    # Gửi refresh token qua cookie (HttpOnly, Secure)
    response.set_cookie(
        "refresh_token",
        refresh_token_data['token'], # Lấy token từ dictionary
        httponly=True,
        secure=True, 
        samesite='None',
        path='/api/auth/tokens' # Chỉ gửi cookie này khi gọi API refresh
    )
    return response

@auth_bp.route('/v2/login', methods=['POST'])
def login_v2():
    """[V2] Đăng nhập, trả về thông tin user đầy đủ (thêm full_name, avatar_url)."""
    data = request.json
    login_identifier = data.get('login')
    password = data.get('password')

    if not all([login_identifier, password]):
        return jsonify({"error": "Login và password là bắt buộc"}), 400

    service = AuthService()
    # [TÁI SỬ DỤNG] Vẫn gọi service y hệt V1
    user, access_token, refresh_token_data, error = service.login_user(login_identifier, password)

    if error:
        return jsonify({"error": error}), 401

    # [V2] Response: Trả về nhiều thông tin hơn
    # (Giả sử model User của bạn có 2 trường 'full_name' và 'avatar_url')
    user_profile_v2 = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "full_name": getattr(user, 'full_name', None), # Dùng getattr để tránh lỗi nếu trường không tồn tại
        "avatar_url": getattr(user, 'avatar_url', None)
    }
    
    response = make_response(jsonify({
        "access_token": access_token,
        "user": user_profile_v2 # Gửi object user v2
    }))
    
    # Gửi refresh token qua cookie (HttpOnly, Secure)
    response.set_cookie(
        "refresh_token",
        refresh_token_data['token'], 
        httponly=True,
        secure=True, 
        samesite='None',
        path='/api/auth/tokens' # Vẫn dùng chung path refresh
    )
    return response

@auth_bp.route('/refresh', methods=['PUT'])
def refresh():
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        return jsonify({"error": "Thiếu refresh token trong cookie"}), 401

    service = AuthService()
    access_token, error = service.refresh_access_token(refresh_token)

    if error:
        return jsonify({"error": error}), 401

    # Có thể set lại cookie mới nếu bạn muốn refresh luôn refresh_token
    response = jsonify({"access_token": access_token})
    return response, 200

@auth_bp.route('/logout', methods=['DELETE'])
def logout():
    data = request.json
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return jsonify({"error": "Refresh token là bắt buộc"}), 400

    service = AuthService()
    success, error = service.logout_user(refresh_token)
    
    if error:
        return jsonify({"error": error}), 401
    
    return jsonify({"message": "Đăng xuất thành công"}), 200

@auth_bp.route('/validate', methods=['POST'])
def validate_token():
    """
    Endpoint NỘI BỘ, chỉ API Gateway được gọi.
    Gateway sẽ gửi access token đến đây để xác thực.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401
    
    access_token = token.split(" ")[1]

    service = AuthService()
    user_data, error = service.validate_access_token(access_token)
    
    if error:
        return jsonify({"error": error, "valid": False}), 401
        
    # Trả về thông tin user cho Gateway
    return jsonify({"valid": True, "user": user_data}), 200


@auth_bp.route("/google/login")
def google_login():
    """Bước 1: Chuyển hướng người dùng đến Google"""

    redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"]
    print("✅ Explicit Redirect URI being sent to Google:", redirect_uri) # In ra để xác nhận


    # ✅ Gọi authorize_redirect để lấy response redirect (302)
    # authlib sẽ dùng redirect_uri này để gửi cho Google
    response = oauth.google.authorize_redirect(redirect_uri)

    # ✅ Force Flask ghi cookie session ngay cả khi là redirect
    # Điều này đảm bảo nonce được lưu trước khi trình duyệt rời đi
    current_app.session_interface.save_session(current_app, session, response)

    return response


@auth_bp.route("/google/callback")
def google_callback():
    """Bước 2: Google redirect về đây"""
    frontend_url = "http://localhost:5174/login"

    try:
        token = oauth.google.authorize_access_token() #Trao đổi code lấy access token (authorize_access_token)
        user_info = token.get('userinfo') # Lấy thông tin user từ Google
        print("✅ User info:", user_info)

        service = OAuthService() # Xử lý thông tin user từ Google
        result = service.handle_google_user(user_info) # Tạo hoặc lấy user từ thông tin Google

        # Gửi dữ liệu user + token về frontend qua redirect
        user_json = quote(json.dumps(result["user"]))
        redirect_url = f"{frontend_url}#accessToken={result['access_token']}&user={user_json}"

        response = make_response(redirect(redirect_url)) 
        response.set_cookie(
            "refresh_token",
            result["refresh_token"], 
            httponly=True,
            secure=False,    # True nếu chạy HTTPS 
            samesite="Lax",  # 'None' nếu frontend khác domain
            path="/api/auth/tokens"
        )
        return response

    except Exception as e:
        print(f"🔥 Google OAuth callback error: {e}")
        return redirect(f"{frontend_url}#error=google_login_failed")
