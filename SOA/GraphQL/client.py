import requests

# Query GraphQL
query = """
{
  allStudents {
    id
    name
    average
    grade
    rlScore
    title
  }
}
"""

url = "http://localhost:5000/graphql"
response = requests.post(url, json={"query": query})

print("Kết quả trả về:")
print(response.json())
