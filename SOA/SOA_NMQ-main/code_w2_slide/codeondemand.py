import requests

url = "http://127.0.0.1:5000/api/code-on-demand"
response = requests.get(url)
data = response.json()
exec(data["script"])  # Thực thi script server gửi

