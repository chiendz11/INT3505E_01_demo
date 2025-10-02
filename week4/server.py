import flask
import json

app = flask.Flask(__name__)

print("Starting server...")
books = {
    1: {"id": 1, "title": "1984", "author": "George Orwell", "available_copies": 6},
    2: {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", "available_copies": 4},
    3: {"id": 3, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "available_copies": 5},
}
users = {1: {"id": 1, "username": "Alice"},
         2: {"id": 2, "username": "Bob"},
         3: {"id": 3, "username": "chienqt"}
}
borrowing_records = {1: {"id": 1, "userId": 3, "bookId": 2, "quantity": 1, "borrowDate": "2023-10-01", }}
returning_records = {1: {"id": 1, "userId": 3, "bookId": 2, "quantity": 1, "returnDate": "2023-10-05"}}

@app.route('/book_list', methods=['GET'])
def list_books():
    return json.dumps(list(books.values())), 200

@app.route('/add_book', methods=['POST'])
def add_book():
    data = flask.request.json
    if not data or 'title' not in data or 'author' not in data or 'available_copies' not in data:
        return {"error": "Invalid input"}, 400
    book_id = len(books) + 1
    books[book_id] = {
        "id": book_id,
        "title": data['title'],
        "author": data['author'],
        "available_copies": data['available_copies']
    }
    return {"message": "Book added", "book_id": book_id}, 201

@app.route('/delete_book/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    if book_id not in books:
        return {"error": "Book not found"}, 404
    del books[book_id]
    return '', 204

@app.route('/update_book/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    if book_id not in books:
        return {"error": "Book not found"}, 404
    data = flask.request.json
    if not data or 'title' not in data or 'author' not in data or 'available_copies' not in data:
        return {"error": "Invalid input"}, 400
    books[book_id] = {
        "id": book_id,
        "title": data['title'],
        "author": data['author'],
        "available_copies": data['available_copies']
    }
    return {"message": "Book updated"}, 200

@app.route('/borrow_book/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    if book_id not in books:
        return {"error": "Book not found"}, 404
    data = flask.request.json
    if not data or 'userId' not in data or 'quantity' not in data:
        return {"error": "Invalid input"}, 404
    user_id = data['userId']
    quantity = data['quantity']
    if books[book_id]['available_copies'] <= quantity:
        return {"error": "No available copies to borrow"}, 400
    else:
        books[book_id]['available_copies'] -= quantity
        record_id = len(borrowing_records) + 1
        borrowing_records[record_id] = {
            "id": record_id,    
            "userId": user_id,
            "bookId": book_id,
            "quantity": quantity,
            "borrowDate": "2023-10-10",  # Example date
        }
        print(f"book's name: {books[book_id]['title']}, available_copies: {books[book_id]['available_copies']}")
        return {"message": "Book borrowed successfully"}, 200
@app.route('/return_book/<int:record_id>', methods=['POST'])
def return_book(record_id):
    data = flask.request.json
    if not data or 'userId' not in data or 'quantity' not in data:
        return {"error": "Invalid input"}, 400
    user_id = data['userId']
    quantity = int(data['quantity'])
    if quantity <= 0:
        return {"error": "Quantity must be greater than 0"}, 400
    elif quantity > borrowing_records[record_id]['quantity']:
        return {"error": "Return quantity larger than borrowed quantity"}, 400
    books[borrowing_records[record_id]['bookId']]['available_copies'] += quantity
    returning_records[len(returning_records) + 1] = {
        "id": len(returning_records) + 1,
        "userId": user_id, 
        "bookId": borrowing_records[record_id]['bookId'], 
        "quantity": quantity,
        "returnDate": "2023-10-10"  # Example date
    }
    print(f"book's name: {books[borrowing_records[record_id]['bookId']]['title']}, available_copies: {books[borrowing_records[record_id]['bookId']]['available_copies']}")
    return {"message": "Book returned successfully"}, 200
if __name__ == '__main__':
    app.run(debug=True, port=5000)