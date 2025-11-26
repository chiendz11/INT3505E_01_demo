# locustfile.py

import random
from locust import HttpUser, task, between

class RealUserBehavior(HttpUser):
    # 1. Cài đặt cơ bản
    # Mỗi user ảo sẽ đợi 1-3 giây giữa các task
    wait_time = between(1, 3)
    host = "http://localhost:8080"  # Thay bằng URL của API Gateway nếu cần
    
    # Biến để lưu token sau khi đăng nhập
    access_token = None

    def on_start(self):
        """
        Đây là hàm chạy 1 LẦN DUY NHẤT khi một user ảo "sinh ra".
        Chúng ta dùng nó để ĐĂNG NHẬP và LẤY TOKEN.
        """
        try:
            # GIẢ SỬ: Bạn đã có user 'user@example.com' / 'password123'
            # trong database test của bạn.
            
            # Lưu ý: Locust đã có self.client để gọi API
            # /api/auth/login là URL trên API Gateway
            response = self.client.post(
                "/api/auth/login", # URL này là URL trên Gateway
                json={"login": "chiendz11", "password": "Bop29042@@5"}
            )
            
            # Báo lỗi nếu login thất bại
            response.raise_for_status() 
            
            data = response.json()
            self.access_token = data.get("access_token")
            
            if not self.access_token:
                print("Lỗi: Không lấy được access_token")
                
        except Exception as e:
            print(f"Lỗi khi đăng nhập: {e}")
            # Dừng user này nếu không login được
            self.environment.runner.quit()


    # 3. Định nghĩa các "Task" (Hành vi)
    
    @task(5) # Gán "trọng số": Task này được chạy nhiều gấp 5 lần
    def get_all_books_paginated(self):
        """
        Hành vi 1: User xem danh sách sách (phân trang)
        """
        if not self.access_token:
            return # Bỏ qua nếu chưa login
            
        # Giả lập user xem các trang ngẫu nhiên
        page = random.randint(1, 5)
        
        self.client.get(
            f"/api/books?page={page}&limit=20",
            headers={"Authorization": f"Bearer {self.access_token}"}
            #
        )

    @task(1) # Gán "trọng số": Task này ít được chạy hơn
    def get_one_book(self):
        """
        Hành vi 2: User xem chi tiết 1 cuốn sách
        """
        if not self.access_token:
            return

        # Giả lập user xem 1 trong 10 sách đầu
        book_id = random.randint(1, 10)
        
        self.client.get(
            f"/api/books/{book_id}",
            name="/api/books/[id]", # Gộp các request này lại 1 nhóm
            headers={"Authorization": f"Bearer {self.access_token}"}
            #
        )