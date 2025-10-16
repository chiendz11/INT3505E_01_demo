import requests
import json

BASE_URL = "http://localhost:5000"

etag_cache = {}
data_cache = {} 

# ==============================
# ⚙️ Helper
# ==============================
def send_request(method: str, endpoint: str, data=None):
    try:
        url = f"{BASE_URL}/{endpoint}"
        headers = {}

        # Nếu có ETag trước đó, gửi lại để kiểm tra thay đổi
        if method == "GET" and url in etag_cache:
            headers['If-None-Match'] = etag_cache[url]

        print(f"\n➡️ {method} {url}")
        if data:
            print(f"📦 Payload: {data}")

        res = requests.request(method, url, json=data, params=data if method == "GET" else None, headers=headers)

        # Xử lý 304 Not Modified
        if res.status_code == 304:
            print("✅ Not Modified (using cached data).")
            # Trả về đối tượng Response "giả" chứa dữ liệu cached
            if url in data_cache:
                # Tạo một đối tượng giả mạo (mock) response để chứa dữ liệu cache
                mock_res = requests.Response()
                mock_res._content = json.dumps(data_cache[url]).encode('utf-8')
                mock_res.status_code = 200 # Đánh dấu là thành công (lấy từ cache)
                return mock_res
            return None # Không có cache data -> vẫn lỗi

        # Xử lý 200 OK (Cập nhật cả ETag và Data)
        if 'ETag' in res.headers:
            etag_cache[url] = res.headers['ETag']
            
        # LƯU DỮ LIỆU VÀO CACHE TRƯỚC KHI TRẢ VỀ
        if res.status_code == 200:
            try:
                data_cache[url] = res.json()
            except json.JSONDecodeError:
                pass # Bỏ qua nếu response không phải JSON
        
        print(f"⬅️ Status: {res.status_code} {res.reason}")
        return res
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


# ==============================
# Book operations
# ==============================
def list_books():
    author = input("Enter author name to filter (leave blank for all): ")
    params = {"author": author} if author else None
    res = send_request("GET", "books", params)
    if not res or res.status_code != 200:
        print("❌ Failed to fetch books.")
        return []

    data = res.json()
    print("\n📚 Available Books:")
    for book in data:
        print(f"  ID: {book['id']} | {book['title']} by {book['author']} | Copies: {book['available_copies']}")
    return data


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
    try:
        book_id = int(input("Enter book ID to view: "))
        res = send_request("GET", f"books/{book_id}")
        if res.status_code == 404:
            print("❌ Book not found.")
            return
        data = res.json()
        print(f"\n📖 Book Details:")
        print(f"  ID: {data['id']}\n  Title: {data['title']}\n  Author: {data['author']}\n  Copies: {data['available_copies']}")
        print("  🔗 HATEOAS Links:")
        for link in data["links"]:
            print(f"   - {link['rel']} [{link['method']}] -> {link['href']}")
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
        if res.status_code == 404:
            print("❌ User not found.")
            return

        data = res.json()
        if not data:
            print("ℹ️ User has no borrowed books.")
            return
        print(f"\n📚 Borrowed Books for User {user_id}:")
        for book in data:
            print(f"  - {book['title']} ({book['author']}) | Qty: {book['borrow_quantity']} | Date: {book['borrow_date']}")
    except ValueError:
        print("❌ Invalid input.")


# ==============================
# Menu
# ==============================
def display_menu():
    print("\n====== Library Management System ======")
    print("1. List all books")
    print("2. Add a new book")
    print("3. Delete a book")
    print("4. Update a book")
    print("5. Get book details")
    print("6. View user's borrowed books")
    print("0. Exit")


def main():
    while True:
        display_menu()
        choice = input("Select an option: ").strip()
        if choice == '1':
            list_books()
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
        elif choice == '0':
            print("👋 Exiting system.")
            break
        else:
            print("❌ Invalid option. Try again.")
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
