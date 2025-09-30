import requests

url = "http://127.0.0.1:5000/api/entries/hello"
response = requests.get(url)  # Sử dụng GET chuẩn
data = response.json()
print("Uniform Interface example:", data)

