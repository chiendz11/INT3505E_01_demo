import requests

url = "http://127.0.0.1:5000/api/entries-hateoas/world"
response = requests.get(url)
data = response.json()

print("Word data:", data["data"])
print("Links sent by server:", data["links"])

related_url = f"http://127.0.0.1:5000{data['links']['related']}"
related_response = requests.get(related_url)
related_data = related_response.json()
print("Related word data:", related_data["data"])
