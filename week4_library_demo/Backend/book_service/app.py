from src import create_app

app = create_app()

if __name__ == '__main__':
    # Chạy app, debug=True chỉ nên dùng khi phát triển
    app.run(host="0.0.0.0", port=5000, debug=True)