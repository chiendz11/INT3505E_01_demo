FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Chạy Gunicorn 4 workers (Production Mode)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src:create_app()"]