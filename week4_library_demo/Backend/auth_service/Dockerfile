FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn
COPY . .
# Auth Service thường chạy cổng 5000 hoặc 5001 (tùy config của bạn)
# Giả sử trong code bạn để 5000, ta cứ expose 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "src:create_app()"]