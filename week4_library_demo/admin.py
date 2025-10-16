import requests
import json

# Đảm bảo BASE_URL khớp với ngrok URL của bạn nếu bạn chạy ở môi trường khác
BASE_URL = "http://localhost:5000"

# Global cache cho ETag và Data. Key sẽ là URL (bao gồm query params)
etag_cache = {}
data_cache = {} 

# ==============================
# ⚙️ Helper
# ==============================
def send_request(method: str, endpoint: str, data=None):
    # Flask GET request sử dụng 'params' thay vì 'json' body
    params = data if method == "GET" and data is not None else None
    json_data = data if method != "GET" else None
    
    url = f"{BASE_URL}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    cache_key = url + ('?' + '&'.join([f"{k}={v}" for k, v in params.items()]) if params else '')
    
    # 1. Nếu có ETag trước đó và là GET, gửi lại để kiểm tra thay đổi
    if method == "GET" and cache_key in etag_cache:
        headers['If-None-Match'] = etag_cache[cache_key]

    print(f"\n➡️ {method} {cache_key}")
    if json_data:
        print(f"📦 Payload: {json_data}")

    try:
        res = requests.request(method, url, json=json_data, params=params, headers=headers)

        # 2. Xử lý 304 Not Modified
        if res.status_code == 304:
            print("✅ Not Modified (using cached data).")
            # Trả về dữ liệu cached
            if cache_key in data_cache:
                # Tạo một đối tượng giả mạo (mock) response để chứa dữ liệu cache
                mock_res = requests.Response()
                # res.url ở đây là URL thật với query params
                mock_res.url = cache_key 
                mock_res._content = json.dumps(data_cache[cache_key]).encode('utf-8')
                mock_res.status_code = 200
                return mock_res
            return None

        # 3. Xử lý 200 OK (Cập nhật cả ETag và Data)
        final_url_key = res.url # Sử dụng URL thực tế mà requests đã gửi (có query params)
        if 'ETag' in res.headers:
            etag_cache[final_url_key] = res.headers['ETag']
            
        if res.status_code == 200:
            try:
                data_cache[final_url_key] = res.json()
            except json.JSONDecodeError:
                pass 
        
        print(f"⬅️ Status: {res.status_code} {res.reason}")
        return res
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


# ==============================
# Book operations (Pagination)
# ==============================
def list_books_offset_pagination():
    """
    Chiến lược 1: OFFSET/LIMIT Pagination (Sử dụng /books?page=X&limit=Y)
    Cũng hỗ trợ lọc theo tác giả.
    """
    print("\n[--- OFFSET/LIMIT PAGINATION (Chiến lược 1) ---]")
    try:
        page = int(input("Enter page number (e.g., 1): "))
        limit = int(input("Enter limit per page (e.g., 10): "))
    except ValueError:
        print("❌ Invalid page or limit.")
        return

    author = input("Enter author name to filter (leave blank for all): ")
    params = {"page": page, "limit": limit}
    if author:
        params["author"] = author

    res = send_request("GET", "books", params)
    if not res or res.status_code != 200:
        print("❌ Failed to fetch books.")
        return

    data = res.json()
    metadata = data.get('metadata', {})
    
    print(f"\n\t*** 📚 Page {metadata.get('page')} of {metadata.get('total_pages')} | Total Records: {metadata.get('total_records')} ***")
    print("\t---------------------------------")
    
    for book in data.get('data', []):
        print(f" \tID: {book['id']} | {book['title']} by {book['author']} | Copies: {book['available_copies']}")

    print("\n\t🔗 Pagination Links (HATEOAS):")
    for rel, href in data.get('links', {}).items():
        print(f"\t - {rel}: {href}")


def list_books_cursor_pagination():
    """
    Chiến lược 2: CURSOR-BASED Pagination (Sử dụng /books/cursor?limit=X&cursor_id=Y)
    Cho phép cuộn vô tận.
    """
    print("\n[--- CURSOR-BASED PAGINATION (Chiến lược 2) ---]")
    try:
        limit = int(input("Enter limit per page (e.g., 15): "))
    except ValueError:
        print("❌ Invalid limit.")
        return
    
    cursor_id = None
    page_num = 1
    
    # Vòng lặp liên tục để lấy trang tiếp theo
    while True:
        params = {"limit": limit}
        if cursor_id is not None:
            params["cursor_id"] = cursor_id

        endpoint = "books/cursor"
        
        print(f"\n\t*** 📚 CURSOR PAGINATION (PAGE {page_num}) ***")
        if cursor_id:
            print(f"\tStarting from cursor_id: {cursor_id}")

        res = send_request("GET", endpoint, params)
        if not res or res.status_code != 200:
            print("❌ Failed to fetch books.")
            break

        data = res.json()
        
        if not data.get('data'):
            print("--- End of data reached. ---")
            break
            
        print("\t---------------------------------")
        for book in data.get('data', []):
            print(f" \tID: {book['id']} | {book['title']} by {book['author']} | Copies: {book['available_copies']}")

        next_cursor = data.get('metadata', {}).get('next_cursor_id')
        
        if not next_cursor or next_cursor == 'end_of_data':
            print("\n--- End of data reached. ---")
            break
        
        cursor_id = next_cursor
        page_num += 1
        
        cont = input("\nPress Enter to fetch next page (or 'q' to quit): ")
        if cont.lower() == 'q':
            break

# ==============================
# Existing Book Operations (Chiến lược 3: Single Resource)
# ==============================
# Lưu ý: Các hàm này không thay đổi nhiều, nhưng đã được thêm vào luồng ứng dụng mới.

def add_book():
    title = input("Enter book title: ")
    if title.lower() == 'q': return
    author = input("Enter book author: ")
    if author.lower() == 'q': return
    try:
        copies = int(input("Enter available copies: "))
        data = {"title": title, "author": author, "available_copies": copies}
        res = send_request("POST", "books", data)
        if res and res.status_code == 201:
            print("✅ Book created successfully.")
    except ValueError:
        print("❌ Invalid number.")


def delete_book():
    try:
        book_id = int(input("Enter book ID to delete: "))
        res = send_request("DELETE", f"books/{book_id}")
        if res.status_code == 204:
            print("✅ Book deleted successfully.")
        elif res.status_code == 404:
            print("❌ Book not found.")
    except ValueError:
        print("❌ Invalid input.")


def update_book():
    try:
        book_id = int(input("Enter book ID to update: "))
        title = input("Enter new title: ")
        author = input("Enter new author: ")
        copies = int(input("Enter new available copies: "))
        data = {"title": title, "author": author, "available_copies": copies}
        res = send_request("PUT", f"books/{book_id}", data)
        if res.status_code == 200:
            print("✅ Book updated successfully.")
        elif res.status_code == 404:
            print("❌ Book not found.")
    except ValueError:
        print("❌ Invalid input.")


def get_book():
    """Chiến lược 3: Lấy 1 bản ghi duy nhất (Single Resource)"""
    print("\n[--- SINGLE RESOURCE RETRIEVAL (Chiến lược 3) ---]")
    try:
        book_id = int(input("Enter book ID to view: "))
        res = send_request("GET", f"books/{book_id}")
        if res and res.status_code == 404:
            print("❌ Book not found.")
            return
        if not res: return
        data = res.json()
        print(f"\n📖 Book Details:")
        print(f" ID: {data['id']}\n Title: {data['title']}\n Author: {data['author']}\n Copies: {data['available_copies']}")
        print(" 🔗 HATEOAS Links:")
        for link in data.get("links", []):
            print(f" - {link['rel']} [{link['method']}] -> {link['href']}")
    except ValueError:
        print("❌ Invalid input.")


# ==============================
# User
# ==============================
def list_user_borrowings():
    try:
        user_id = int(input("Enter User ID to view borrowings: "))

        # 🔹 đổi endpoint sang /users/{id}/books?relation=borrowed
        endpoint = f"users/{user_id}/books"
        params = {"relation": "borrowed"}

        res = send_request("GET", endpoint, params)
        if not res:
            print("❌ Request failed.")
            return
        # Giả định User luôn tồn tại trong DB, nếu không có book thì trả về []
        if res.status_code != 200:
            print(f"❌ Failed to fetch user borrowings: {res.status_code}")
            return

        data = res.json()
        if not data:
            print("ℹ️ User has no borrowed books.")
            return
        print(f"\n📚 Borrowed Books for User {user_id}:")
        for book in data:
            # Lưu ý: Các field ở đây có thể cần được điều chỉnh nếu DB schema khác
            print(f" - {book.get('title')} ({book.get('author')}) | Qty: {book.get('quantity')} | Date: {book.get('date')}")
    except ValueError:
        print("❌ Invalid input.")


# ==============================
# Menu
# ==============================
def display_menu():
    print("\n====== Library Management System ======")
    print("--- Book Management ---")
    print("2. Add a new book")
    print("3. Delete a book")
    print("4. Update a book")
    print("5. Get book details (Single Resource)")
    print("--- Pagination Strategies ---")
    print("1. View Books (Offset/Limit Pagination - Phân trang theo trang)")
    print("7. View Books (Cursor-based Pagination - Cuộn vô tận)")
    print("--- Transaction/User ---")
    print("6. View user's borrowed books")
    print("0. Exit")


def main():
    while True:
        display_menu()
        choice = input("Select an option: ").strip()
        if choice == '1':
            list_books_offset_pagination()
        elif choice == '2':
            add_book()
        elif choice == '3':
            delete_book()
        elif choice == '4':
            update_book()
        elif choice == '5':
            get_book()
        elif choice == '6':
            list_user_borrowings()
        elif choice == '7':
            list_books_cursor_pagination()
        elif choice == '0':
            print("👋 Exiting system.")
            break
        else:
            print("❌ Invalid option. Try again.")
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
