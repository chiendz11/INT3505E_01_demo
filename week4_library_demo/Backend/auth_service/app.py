from src import create_app

app = create_app()

if __name__ == '__main__':
    # Chạy trên port 5002
    app.run(debug=True, port=5002)
