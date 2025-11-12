from src import create_app

app = create_app()

if __name__ == '__main__':
    # Mở một đường hầm HTTP đến port 8080
    # bind_tls=True có nghĩa là bạn muốn public URL là "https" (khuyên dùng)
    app.run(host="0.0.0.0", port=8080, debug=True)