import requests
import json
from admin import list_books

BASE_URL = "http://localhost:5000"
USERID = 3  # Assuming user ID is known or retrieved after login
RECORDID = 1  # Assuming record ID is known or retrieved after borrowing
def send_request(method: str, endpoint: str, data: None):
    try:
        url = f"{BASE_URL}/{endpoint}"
        print(f"Sending {method} request to {url} with data: {data}")
        if method == "GET":
            response = requests.get(url) 
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        elif method == "PUT":
            response = requests.put(url, json=data)
        else: 
            raise ValueError("Unsupported HTTP method")
        print(f"Response Status Code: {response.status_code}")
        return response
        
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
def borrow_book():
    while True:
        print("Available Books:")
        data = list_books()
        book_id = input("Enter book ID to borrow or q to quit: ")
        if book_id.lower() == 'q':
            break
        elif book_id not in [str(book['id']) for book in data]:
            print("Invalid book ID. Please try again.")
            continue
        quantity = input("Enter your book quantity or q to quit: ")
        if quantity.lower() == 'q':
            break
        try:
            book_id = int(book_id)
            quantity = int(quantity)
            res = send_request('POST', f'borrow_book/{book_id}', data = {"userId": USERID, "quantity": quantity})
            if res and res.status_code == 200:
                print("Book borrowed successfully.")
                break
            elif res and res.status_code == 400:
                print(f"Error: {res['error']}")
                continue
            elif res and res.status_code == 404:
                print(f"Error: {res['error']}. Please try again.")
                continue
        except ValueError:
            print("Invalid book ID or book number. Please enter a number.")
            continue
def return_book():
    while True: 
        quantity = input("Enter your book quantity or q to quit: ")
        if quantity.lower() == 'q':
            break
        try:
            res = send_request('POST', f'return_book/{RECORDID}', data = {"userId": USERID, "quantity": quantity})
            if res and res.status_code == 200:
                print("Book returned successfully.")
                break
            elif res and res.status_code == 400:
                print(f"Error: {res['error']}. Please try again.")
                continue
        except ValueError:
            print("Invalid book number. Please enter a number.")

def display_menu():
    print("\nLibrary Management System")
    print("1. Borrow Book")
    print("2. Return Book")
    print("0. Exit")

def main():
    while True:
        display_menu()
        choice = input("Select an option: ")
        if choice == '1':
            borrow_book()
        elif choice == '2':
            return_book()
        elif choice == '0':
            print("Exiting the system.")
            break
        else:
            print("Invalid choice. Please try again.")
        print("\nPress Enter to continue...")
if __name__ == "__main__":
    main()