import requests
import json
from admin import list_books  # Hàm này phải trả về list sách từ server

BASE_URL = "http://localhost:5000"
USER_ID = 3  # User đăng nhập giả định

# ==========================================================
# 🔧 Hàm gửi request chung
# ==========================================================
def send_request(method: str, endpoint: str, data=None):
    try:
        url = f"{BASE_URL}/{endpoint}"
        print(f"\n➡️ Sending {method} request to {url}")
        if data:
            print(f"   Data: {data}")

        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError("Unsupported HTTP method")

        print(f"⬅️ Response [{response.status_code}]: {response.text}\n")
        return response

    except requests.RequestException as e:
        print(f"⚠️ Request failed: {e}")
        return None


# ==========================================================
# 📖 Mượn sách
# ==========================================================
def borrow_book():
    while True:
        print("\n📚 Available Books:")
        data = list_books()  # Hàm này phải gọi GET /books và trả về list
        if not data:
            print("No books found.")
            return

        for book in data:
            print(f"  ID: {book['id']} | {book['title']} by {book['author']} (copies: {book['available_copies']})")

        book_id = input("\nEnter book ID to borrow (or 'q' to quit): ")
        if book_id.lower() == 'q':
            break

        if not any(str(book['id']) == book_id for book in data):
            print("❌ Invalid book ID. Please try again.")
            continue

        quantity = input("Enter quantity to borrow (or 'q' to quit): ")
        if quantity.lower() == 'q':
            break

        try:
            book_id = int(book_id)
            quantity = int(quantity)
            res = send_request(
                'POST',
                'borrowings',
                data={"userId": USER_ID, "bookId": book_id, "quantity": quantity}
            )

            if not res:
                continue
            if res.status_code == 201:
                print("✅ Book borrowed successfully.")
                break
            else:
                try:
                    print(f"⚠️ Error: {res.json().get('error', 'Unknown error')}")
                except:
                    print("⚠️ Unexpected server response.")
        except ValueError:
            print("❌ Please enter a valid number for book ID and quantity.")


# ==========================================================
# 📦 Trả sách
# ==========================================================
def return_book():
    while True:
        print("\n📖 Your borrowed books:")
        res = send_request("GET", f"users/{USER_ID}/borrowings", data=None)
        if not res or res.status_code != 200:
            print("⚠️ Could not retrieve borrow list.")
            return

        borrowed_books = res.json()
        if not borrowed_books:
            print("You have not borrowed any books.")
            return

        for b in borrowed_books:
            print(f"  ID: {b['id']} | {b['title']} (borrowed: {b['borrow_quantity']})")

        book_id = input("\nEnter book ID to return (or 'q' to quit): ")
        if book_id.lower() == 'q':
            break

        if not any(str(b['id']) == book_id for b in borrowed_books):
            print("❌ Invalid book ID. Try again.")
            continue

        quantity = input("Enter quantity to return (or 'q' to quit): ")
        if quantity.lower() == 'q':
            break

        try:
            book_id = int(book_id)
            quantity = int(quantity)
            res = send_request(
                'POST',
                'returns',
                data={"userId": USER_ID, "bookId": book_id, "quantity": quantity}
            )

            if not res:
                continue
            if res.status_code == 201:
                print("✅ Book returned successfully.")
                break
            else:
                try:
                    print(f"⚠️ Error: {res.json().get('error', 'Unknown error')}")
                except:
                    print("⚠️ Unexpected server response.")
        except ValueError:
            print("❌ Invalid number. Please try again.")


# ==========================================================
# 🧭 Menu chính
# ==========================================================
def display_menu():
    print("\n====== Library Management System ======")
    print("1. Borrow Book")
    print("2. Return Book")
    print("0. Exit")
    print("=======================================")


def main():
    while True:
        display_menu()
        choice = input("Select an option: ").strip()
        if choice == '1':
            borrow_book()
        elif choice == '2':
            return_book()
        elif choice == '0':
            print("👋 Exiting the system.")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
