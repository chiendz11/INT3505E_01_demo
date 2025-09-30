import requests

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "29042005"

headers = {
    "x-api-key": API_KEY,
    "User-Agent": "TestClient/1.0",
    "Accept": "application/json"
}
def print_response(res : requests.Response):
    print("status code:", res.status_code, "\n")
    try:
        print("response:", res.json(), "\n")
    except:
        print("response:", res.text, "\n")
    print("headers:", res.headers, "\n")
def test_api():
    print("=== GET all students ===")
    res = requests.get(f"{BASE_URL}/students", headers=headers)
    print_response(res)

    print("=== GET student id=1 ===")
    res = requests.get(f"{BASE_URL}/students/1", headers=headers)
    print_response(res)
    

    print("=== POST create new student ===")
    new_student = {"id": 4, "name": "Bui Anh Chien", "age": 20, "grade": "CA4", "address": "Ha Noi"}
    res = requests.post(f"{BASE_URL}/students", json=new_student, headers=headers)
    print_response(res)
    

    print("=== PUT update student id=4 ===")
    updated_student = {"id": 4, "name": "Bui Anh Chien Updated", "age": 21, "grade": "CA4", "address": "Ha Noi"}
    res = requests.put(f"{BASE_URL}/students/4", json=updated_student, headers=headers)
    print_response(res)
    

    print("=== PATCH update student id=4 ===")
    patch_data = {"grade": "CS4"}
    res = requests.patch(f"{BASE_URL}/students/4", json=patch_data, headers=headers)
    print_response(res)

    print("=== DELETE student id=4 ===")
    res = requests.delete(f"{BASE_URL}/students/4", headers=headers)
    print_response(res)


if __name__ == "__main__":
    test_api()
