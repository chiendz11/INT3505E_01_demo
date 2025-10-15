from flask import Flask, make_response, request
import json

app = Flask(__name__)

print("Starting server...")

# ==============================
# 🧠 Mock Database
# ==============================
books = {
    1: {"id": 1, "title": "1984", "author": "George Orwell", "available_copies": 6},
    2: {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", "available_copies": 4},
    3: {"id": 3, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "available_copies": 5},
}

users = {
    1: {"id": 1, "username": "Alice"},
    2: {"id": 2, "username": "Bob"},
    3: {"id": 3, "username": "Chienqt"}
}

transactions = {
    1: {"id": 1, "userId": 3, "bookId": 2, "quantity": 1, "type": "borrow", "date": "2023-10-01"},
    2: {"id": 2, "userId": 3, "bookId": 2, "quantity": 1, "type": "return", "date": "2023-10-05"}
}

BASE_URL = "http://localhost:5000"

# ==============================
# ⚙️ HATEOAS Helper
# ==============================
def add_hateoas_book(book):
    """Thêm link HATEOAS cho resource Book"""
    book['links'] = [
        {"rel": "self", "href": f"{BASE_URL}/books/{book['id']}", "method": "GET"},
        {"rel": "update", "href": f"{BASE_URL}/books/{book['id']}", "method": "PUT"},
        {"rel": "delete", "href": f"{BASE_URL}/books/{book['id']}", "method": "DELETE"},
        {"rel": "borrow", "href": f"{BASE_URL}/transactions", "method": "POST"}
    ]
    return book

# ==============================
# 📚 Book API
# ==============================
@app.route('/books', methods=['GET'])
def list_books():
    """Lấy danh sách tất cả sách, có thể lọc theo tác giả"""
    author_filter = request.args.get('author')
    result = list(books.values())

    if author_filter:
        result = [b for b in result if b['author'].lower() == author_filter.lower()]

    response = make_response(json.dumps(result), 200)
    response.headers['Cache-Control'] = 'public, max-age=60'
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    if book_id not in books:
        return {"error": "Book not found"}, 404
    return add_hateoas_book(books[book_id].copy()), 200


@app.route('/books', methods=['POST'])
def create_book():
    data = request.json
    if not data or not all(k in data for k in ('title', 'author', 'available_copies')):
        return {"error": "Invalid input"}, 400

    book_id = len(books) + 1
    books[book_id] = {
        "id": book_id,
        "title": data['title'],
        "author": data['author'],
        "available_copies": data['available_copies']
    }
    return {"message": "Book created", "book_id": book_id}, 201


@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    if book_id not in books:
        return {"error": "Book not found"}, 404
    data = request.json
    if not data or not all(k in data for k in ('title', 'author', 'available_copies')):
        return {"error": "Invalid input"}, 400

    books[book_id].update(data)
    return {"message": "Book updated successfully"}, 200


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    if book_id not in books:
        return {"error": "Book not found"}, 404
    del books[book_id]
    return '', 204


# ==============================
# 🔁 Transaction API
# ==============================
@app.route('/transactions', methods=['POST'])
def create_transaction():
    """Tạo một giao dịch mượn hoặc trả sách"""
    data = request.json
    if not data or not all(k in data for k in ('userId', 'bookId', 'quantity', 'type')):
        return {"error": "Invalid input"}, 400

    user_id = data['userId']
    book_id = data['bookId']
    quantity = data['quantity']
    tran_type = data['type']

    if user_id not in users or book_id not in books:
        return {"error": "User or book not found"}, 404
    if tran_type not in ['borrow', 'return']:
        return {"error": "Invalid transaction type"}, 400

    if tran_type == 'borrow':
        if books[book_id]['available_copies'] < quantity:
            return {"error": "Not enough copies available"}, 400
        books[book_id]['available_copies'] -= quantity
    elif tran_type == 'return':
        books[book_id]['available_copies'] += quantity

    tran_id = len(transactions) + 1
    transactions[tran_id] = {
        "id": tran_id,
        "userId": user_id,
        "bookId": book_id,
        "quantity": quantity,
        "type": tran_type,
        "date": "2023-10-10"
    }

    return {"message": "Transaction recorded successfully", "transaction_id": tran_id}, 201


# ==============================
# 👤 User API
# ==============================
@app.route('/users/<int:user_id>/books', methods=['GET'])
def list_user_books(user_id):
    """Lấy danh sách các sách mà người dùng đã mượn hoặc trả"""
    if user_id not in users:
        return {"error": "User not found"}, 404

    relation = request.args.get('relation', 'borrowed')
    if relation not in ['borrowed', 'returned']:
        return {"error": "Invalid relation type"}, 400

    tran_type = 'borrow' if relation == 'borrowed' else 'return'

    filtered_transactions = [
        t for t in transactions.values()
        if t['userId'] == user_id and t['type'] == tran_type
    ]

    result = []
    for t in filtered_transactions:
        if t['bookId'] in books:
            book_info = books[t['bookId']].copy()
            book_info.update({
                "transaction_type": t['type'],
                "quantity": t['quantity'],
                "date": t['date']
            })
            result.append(book_info)

    response = make_response(json.dumps(result), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


# ==============================
# 🚀 Run
# ==============================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
