import requests

url = "http://127.0.0.1:5000/api/entries/world"
response = requests.get(url)
data = response.json()
print("Client-Server: ", data)


