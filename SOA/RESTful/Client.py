import requests
import json

# Endpoint RESTful chuyên biệt đã được thiết kế để trả về bản tóm tắt hiệu suất.
# Endpoint này thay thế cho Query GraphQL của bạn.
url = "http://127.0.0.1:8000/students/performance_summary"

try:
    # 1. Gửi yêu cầu GET
    # Trong REST, yêu cầu GET đến endpoint này sẽ tự động trả về 
    # các trường đã được lọc và tính toán (name, gpa, rl_score, evaluation)
    response = requests.get(url)

    # 2. Kiểm tra mã trạng thái
    response.raise_for_status() # Báo lỗi nếu mã trạng thái là 4xx hoặc 5xx

    # 3. Phân tích phản hồi JSON
    data = response.json()

    print("Kết quả trả về (RESTful API):")
    print("-" * 50)
    
    # 4. Hiển thị dữ liệu đã lọc và tính toán
    for student in data:
        print(f"ID: {student['id']}, Tên: {student['name']}")
        print(f"  > ĐTB: {student['gpa']}, ĐRL: {student['rl_score']}")
        print(f"  > Đánh giá: {student['evaluation']}")
        print("-" * 50)

except requests.exceptions.RequestException as e:
    print(f"Lỗi khi gọi API: {e}")
    print("Vui lòng đảm bảo Server FastAPI đang chạy tại http://127.0.0.1:8000")