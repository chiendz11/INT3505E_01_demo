import requests
import time

url = "http://127.0.0.1:5000/api/entries-cache/hello"

# Lần 1: request server
response1 = requests.get(url)
data1 = response1.json()
print("Data1:", data1)
print("Cache-Control header:", response1.headers.get("Cache-Control"))

# Lần 2: request lại sau 5 giây
time.sleep(5)
response2 = requests.get(url)
data2 = response2.json()
print("Data2:", data2)
print("Cache-Control header:", response2.headers.get("Cache-Control"))
