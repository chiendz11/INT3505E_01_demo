import random
from locust import HttpUser, task, between

# Biến toàn cục để lưu ID sách được tạo ra,
# dùng cho các yêu cầu GET, PUT, DELETE.
# *Lưu ý: Trong môi trường thực tế, nên dùng Locust's 'self.environment.catch_response'*
# *hoặc cơ chế biến môi trường (Environment variables) phức tạp hơn.*
book_ids_to_clean_up = []

class BookAPIUser(HttpUser):
    """
    Một người dùng mô phỏng hoạt động với Book API.
    """
    # Thời gian chờ giữa các lần thực hiện tác vụ (tính bằng giây)
    wait_time = between(1, 3) 
    # Địa chỉ cơ sở của API (thay đổi nếu cần)
    host = "http://127.0.0.1:8080" 

    @task(3) # Tần suất cao nhất (3)
    def create_book(self):
        """
        Tạo một cuốn sách mới (POST /books).
        Sau khi tạo, lưu book_id để có thể dùng cho các thao tác khác.
        """
        # Tạo dữ liệu sách ngẫu nhiên
        book_data = {
            "title": f"Test Book {random.randint(1000, 9999)}",
            "author": "Locust User",
            "year": random.randint(1990, 2023),
            "copies": random.randint(1, 10)
        }

        # Dùng `with self.client.post(...) as response:` để kiểm soát phản hồi
        # và trích xuất dữ liệu, ngay cả khi có lỗi HTTP.
        with self.client.post(
            "/books", 
            json=book_data, 
            name="/books [POST]", 
            catch_response=True
        ) as response:
            if response.status_code == 201:
                try:
                    # Trích xuất book_id từ JSON response
                    new_book_id = response.json().get("book_id")
                    if new_book_id is not None:
                        # Lưu ID vào danh sách để dùng cho các tasks khác
                        book_ids_to_clean_up.append(new_book_id)
                        response.success()
                    else:
                        response.failure("Book ID not found in 201 response")
                except Exception as e:
                    response.failure(f"Failed to parse JSON for book_id: {e}")
            else:
                response.failure(f"Failed to create book with status code {response.status_code}")

    @task(5) # Tần suất cao (5) - Mô phỏng việc đọc dữ liệu thường xuyên
    def list_books(self):
        """
        Lấy danh sách sách có phân trang (GET /books).
        Sử dụng phân trang kiểu offset.
        """
        limit = random.choice([10, 20])
        page = random.randint(1, 5) # Lấy ngẫu nhiên trang 1 đến 5
        self.client.get(
            f"/books?limit={limit}&page={page}", 
            name="/books?limit=X&page=Y [GET]"
        )

    @task(2) # Tần suất thấp (2)
    def get_book_by_id(self):
        """
        Lấy thông tin một cuốn sách cụ thể (GET /books/{id}).
        Chỉ thực hiện nếu có ID sách đã được tạo.
        """
        if book_ids_to_clean_up:
            # Chọn ngẫu nhiên một ID sách đã được tạo
            book_id = random.choice(book_ids_to_clean_up)
            self.client.get(f"/books/{book_id}", name="/books/{id} [GET]")

    @task(1) # Tần suất thấp nhất (1)
    def update_book(self):
        """
        Cập nhật một cuốn sách (PUT /books/{id}).
        Chỉ thực hiện nếu có ID sách đã được tạo.
        """
        if book_ids_to_clean_up:
            book_id = random.choice(book_ids_to_clean_up)
            update_data = {
                "copies": random.randint(11, 20) # Cập nhật số lượng bản sao
            }
            self.client.put(
                f"/books/{book_id}", 
                json=update_data, 
                name="/books/{id} [PUT]"
            )

    # @task(0) # Có thể bỏ qua hoặc để tần suất rất thấp (0)
    # def delete_book(self):
    #     """
    #     Xóa một cuốn sách (DELETE /books/{id}).
    #     Để giữ cho việc kiểm thử đơn giản, ta tạm thời không xóa 
    #     để tránh lỗi 404 cho các tasks khác. Nếu muốn kiểm thử DELETE, 
    #     bạn có thể bỏ comment và tăng tần suất.
    #     """
    #     if book_ids_to_clean_up:
    #         book_id_to_delete = book_ids_to_clean_up.pop(0) # Xóa sách cũ nhất
    #         self.client.delete(f"/books/{book_id_to_delete}", name="/books/{id} [DELETE]")