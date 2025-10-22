from src import create_app
from pyngrok import ngrok, conf # 👈 Thêm 2 dòng này
import os



app = create_app()

if __name__ == '__main__':
    # Mở một đường hầm HTTP đến port 8080
    # bind_tls=True có nghĩa là bạn muốn public URL là "https" (khuyên dùng)
    http_tunnel = ngrok.connect(8080, bind_tls=True)
    
    print("="*50)
    print(f"✅ API Gateway đang chạy tại: http://localhost:8080")
    print(f"✅ Swagger UI Public URL (ngrok): {http_tunnel.public_url}") 
    print("="*50)

    # Chạy app Flask của bạn
    # Tắt "debug=True" trong production, 
    # nhưng bật "allow_unsafe_werkzeug=True" để chạy với ngrok
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)