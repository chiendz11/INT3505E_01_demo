from src import create_app

app = create_app()

if __name__ == '__main__':
    # Chạy trên một port mới, ví dụ 5003
    app.run(host="0.0.0.0", port=5003, debug=True)
