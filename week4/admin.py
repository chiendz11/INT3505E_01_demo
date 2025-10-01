import requests
import json

BASE_URL = 'http://localhost:5000'

def send_request(method: str, endpoint: str, data: None):
    try:
        url = f"{BASE_URL}/{endpoint}"
        print(f"Sending {method} request to {url} with data: {data}")
        if method == 'GET':
            response = requests.get(url) 
        elif method == 'POST':
            response = requests.post(url, json=data)
        elif method == 'DELETE':
            response = requests.delete(url)
        elif method == 'PUT':
            response = requests.put(url, json=data)
        else: 
            raise ValueError("Unsupported HTTP method")
        print(f"Response Status Code: {response.status_code}/{response.reason}")
        return response.json()
        
    except requests.RequestException as e:
        return None
    
def list_books():
    res = send_request('GET', 'book_list', None)
    print("Available Books:")
    for book in res:
        print(f"ID: {book['id']}, Title: {book['title']}, Author: {book['author']}, Available Copies: {book['available_copies']}")
    return res

def add_book():
    title = input("Enter book title or 'q' to quit: ")
    if title.lower() == 'q':
        return
    author = input("Enter book author: ")
    if author.lower() == 'q':
        return
    available_copies = input("Enter number of available copies: ")
    if available_copies.lower() == 'q':
        return
    try:
        available_copies = int(available_copies)
        book_data = {
            "title": title,
            "author": author,
            "available_copies": available_copies
        }
        send_request('POST', 'add_book', book_data)
    except ValueError:
        print("Invalid number for available copies.")
        return

def delete_book():
    while True:
        book_id = input("Enter book ID to delete or q to quit: ")
        if book_id.lower() == 'q':
            break
        try:
            book_id = int(book_id)
            res = send_request('DELETE', f'delete_book/{book_id}', None)
            if res.status_code == 204:
                print("Book deleted successfully.")
                break
            elif res.status_code == 404:
                print(f"{res.message}")
                continue
        except ValueError:
            print("Invalid book ID. Please enter a number.")
            continue

def update_book():
    while True:
        book_id = input("Enter book ID to update or q to quit: ")
        if book_id.lower() == 'q':
            break
        try:
            book_id = int(book_id)
            title = input("Enter new title: ")
            if title.lower() == 'q':
                return
            author = input("Enter new author: ")
            if author.lower() == 'q':
                return
            available_copies = input("Enter new number of available copies: ")
            if available_copies.lower() == 'q':
                return
            available_copies = int(available_copies)
            book_data = {
                "title": title,
                "author": author,
                "available_copies": available_copies
            }
            res = send_request('PUT', f'update_book/{book_id}', book_data)
            if res and res.status_code == 200:
                print("Book updated successfully.")
                break
            elif res and res.status_code == 404:
                print("Book not found.")
                continue
        except ValueError:
            print("Invalid input. Please enter valid data.")
            continue 

def display_menu():
    print("\nLibrary Management System")
    print("1. List all books")
    print("2. Add a new book")
    print("3. Delete a book")
    print("4. Update a book")
    print("0. Exit")

def main():
    while True:
        display_menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            list_books()
        elif choice == '2':
            add_book()
        elif choice == '3':
            delete_book()
        elif choice == '4':
            update_book()
        elif choice == '0':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")
        print("\nPress Enter to continue...")
if __name__ == "__main__":
    main()
