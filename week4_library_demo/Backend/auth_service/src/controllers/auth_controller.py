import json
from flask import Blueprint, request, jsonify, current_app, make_response, redirect, session
from ..services.auth_service import AuthService
from ..services.oauth_service import oauth, OAuthService
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/users', methods=['POST'])
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
        path='/api/auth' # Chỉ gửi cookie này khi gọi API refresh
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

# ==================================
# LOGIN V3 (Thay đổi kiểu dữ liệu)
# ==================================
@auth_bp.route('/v3/login', methods=['POST'])
def login_v3():
    """[V3] Breaking Change: Thay đổi kiểu dữ liệu 'user.id' từ String -> Integer."""
    data = request.json
    login_identifier = data.get('login')
    password = data.get('password')
    if not all([login_identifier, password]):
        return jsonify({"error": "Login và password là bắt buộc"}), 400

    service = AuthService()
    user, access_token, refresh_token_data, error = service.login_user(login_identifier, password)
    if error:
        return jsonify({"error": error}), 401

    # [V3] Response: Thay đổi kiểu dữ liệu
    # Client V1/V2 sẽ bị lỗi nếu cố parse ID này thành String UUID
    user_profile_v3 = {
        "id": 12345, # Giả lập ID kiểu Integer, thay vì user.id (String)
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "full_name": getattr(user, 'full_name', None),
        "avatar_url": getattr(user, 'avatar_url', None)
    }
    response = make_response(jsonify({ "access_token": access_token, "user": user_profile_v3 }))
    response.set_cookie( "refresh_token", refresh_token_data['token'], ...) # Set cookie
    return response

# ==================================
# LOGIN V4 (Thay đổi cấu trúc response)
# ==================================
@auth_bp.route('/v4/login', methods=['POST'])
def login_v4():
    """[V4] Breaking Change: Thay đổi cấu trúc (nesting) và trả refresh_token trong body."""
    data = request.json
    login_identifier = data.get('login')
    password = data.get('password')
    if not all([login_identifier, password]):
        return jsonify({"error": "Login và password là bắt buộc"}), 400

    service = AuthService()
    user, access_token, refresh_token_data, error = service.login_user(login_identifier, password)
    if error:
        return jsonify({"error": error}), 401

    # [V4] Response: Cấu trúc lồng nhau hoàn toàn mới
    # Client V1/V2/V3 sẽ lỗi vì không tìm thấy 'access_token' ở cấp root
    response_data = {
        "data": {
            "tokens": {
                "access": access_token,
                "refresh": refresh_token_data['token'] # Trả refresh_token trong body
            },
            "profile": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role
            }
        }
    }
    
    # [V4] Không set cookie nữa
    response = make_response(jsonify(response_data))
    return response

# ==================================
# LOGIN V5 (Thay đổi cấu trúc request)
# ==================================
@auth_bp.route('/v5/login', methods=['POST'])
def login_v5():
    """[V5] Breaking Change: Bắt buộc phải có 'device_id' trong request body."""
    data = request.json
    login_identifier = data.get('login')
    password = data.get('password')
    device_id = data.get('device_id') # Trường mới

    # [V5] Kiểm tra trường request mới
    if not all([login_identifier, password, device_id]):
        return jsonify({"error": "Login, password, và device_id là bắt buộc"}), 400

    # Client V1->V4 gọi V5 sẽ bị lỗi 400 ở trên
    
    service = AuthService()
    user, access_token, refresh_token_data, error = service.login_user(login_identifier, password)
    if error:
        return jsonify({"error": error}), 401

    print(f"✅ [Auth V5] Ghi nhận đăng nhập từ device: {device_id}")

    # [V5] Response: Có thể dùng lại cấu trúc V2
    user_profile_v2 = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "full_name": getattr(user, 'full_name', None),
        "avatar_url": getattr(user, 'avatar_url', None)
    }
    response = make_response(jsonify({ "access_token": access_token, "user": user_profile_v2 }))
    response.set_cookie( "refresh_token", refresh_token_data['token'], ...) # Set cookie
    return response

@auth_bp.route('/refresh-token', methods=['PUT'])
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
    refresh_token = request.cookies.get('refresh_token')
    print(f"🔥 [DEBUG /logout] Cookie nhận được: {refresh_token}")
    print(f"🔥 [DEBUG /logout] Key đang dùng: {current_app.config.get('JWT_REFRESH_SECRET_KEY')}")
    if not refresh_token:
        return jsonify({"error": "Refresh token (cookie) không tìm thấy"}), 401

    service = AuthService()
    
    # ✅ Sửa dòng này để nhận 2 giá trị
    success, error = service.logout_user(refresh_token) 
    
    if not success: # Hoặc 'if error:'
        print(f"Lỗi khi revoke token: {error}")
        
    response = make_response(jsonify({"message": "Đăng xuất thành công"}), 200)
    
    # Gửi lệnh cho trình duyệt xóa cookie
    response.delete_cookie(
        "refresh_token",
        path='/api/auth', # Path phải khớp với lúc set
        secure=True,
        httponly=True,
        samesite='None'
    )
    
    return response

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
    """Bước 1: Chuyển hướng người dùng đến Google (ĐÃ THÊM PKCE)"""

    redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"]
    print("✅ Explicit Redirect URI being sent to Google:", redirect_uri)

    # ✅ [SỬA DÒNG NÀY] Thêm code_challenge_method='S256'
    # authlib sẽ tự động tạo 'code_verifier', 'code_challenge', 
    # lưu 'code_verifier' vào session, và gửi 'code_challenge' cho Google.
    response = oauth.google.authorize_redirect(
        redirect_uri, 
        code_challenge_method='S256' 
    )

    current_app.session_interface.save_session(current_app, session, response)
    return response


@auth_bp.route("/google/callback")
def google_callback():
    """Bước 2: Google redirect về đây (KHÔNG CẦN SỬA)"""
    frontend_url = "http://localhost:5174/login" # Giả sử đây là URL của FE

    try:
        # ✅ KHÔNG CẦN THAY ĐỔI
        # authlib đủ thông minh để tự động
        # lấy 'code_verifier' từ session và gửi kèm theo (code + verifier)
        # để đổi lấy access token.
        token = oauth.google.authorize_access_token() 
        
        user_info = token.get('userinfo') 
        print("✅ User info:", user_info)

        service = OAuthService() 
        result = service.handle_google_user(user_info) 

        # Gửi dữ liệu user + token về frontend qua redirect
        user_json = quote(json.dumps(result["user"]))
        redirect_url = f"{frontend_url}#accessToken={result['access_token']}&user={user_json}"

        response = make_response(redirect(redirect_url)) 
        
        # Sửa lại path cookie cho đúng
        response.set_cookie(
            "refresh_token",
            result["refresh_token"], 
            httponly=True,
            secure=True,     # True nếu chạy HTTPS 
            samesite="None",   # 'None' nếu frontend khác domain
            path="/api/auth" # Path cha để /logout và /refresh dùng được
        )
        return response

    except Exception as e:
        print(f"🔥 Google OAuth callback error: {e}")
        return redirect(f"{frontend_url}#error=google_login_failed")

    
@auth_bp.route('/users/nplus1', methods=['GET'])
def debug_users_nplus1():
    """❌ Gây ra N+1 Query Problem"""
    service = AuthService()
    result = service.get_users_with_nplus1()
    return jsonify(result), 200


@auth_bp.route('/users/eager', methods=['GET'])
def debug_users_eager():
    """✅ Giải pháp: Eager Loading"""
    service = AuthService()
    result = service.get_users_with_eager_loading()
    return jsonify(result), 200


@auth_bp.route('/users/batch', methods=['GET'])
def debug_users_batch():
    """✅ Giải pháp: Batch Loading"""
    service = AuthService()
    result = service.get_users_with_batch_loading()
    return jsonify(result), 200
