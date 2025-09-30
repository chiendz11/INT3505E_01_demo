from fastapi import FastAPI, Request, Header, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI()

# Fake DB
students_db = {
    1: {"id": 1, "name": "Nguyen Van A", "age": 16, "grade": "10A1", "address": "Hanoi"},
    2: {"id": 2, "name": "Tran Thi B", "age": 17, "grade": "11B2", "address": "Da Nang"},
    3: {"id": 3, "name": "Le Van C", "age": 15, "grade": "9C3", "address": "Ho Chi Minh City"}
}

# API Key
API_KEY = "29042005"
MAX_REQUESTS = 5
request_count = 0
WAIT_TIME = 10 # seconds
last_reset_time = datetime.utcnow()

# Student model
class Student(BaseModel):
    id: int
    name: str
    age: int
    grade: str
    address: str


# Middleware để thêm General & Response headers
@app.middleware("http")
async def add_headers(request: Request, call_next):
    global request_count
    global last_reset_time
    current_time = datetime.utcnow()
    retry_after = current_time + timedelta(seconds=WAIT_TIME)
    retry_after_str = retry_after.strftime("%a, %d %b %Y %H:%M:%S GMT")
    

    if current_time - last_reset_time > timedelta(seconds=WAIT_TIME):
        request_count = 0
        last_reset_time = current_time
        print(f"Request count reset at {last_reset_time}")

    request_count += 1
    # Rate limiting
    if request_count > MAX_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests"},
            headers={
                "Date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "Connection": "close",
                "Server": "FastAPI Server",
                "Cache-Control": "no-cache",
                "Content-Type": "application/json",
                "X-RateLimit-Limit": str(MAX_REQUESTS),
                "X-RateLimit-Remaining": "0",
                "Retry-After": retry_after_str
            }
        )

    response: Response = await call_next(request)

    # Thêm General & Response headers
    response.headers["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.headers["Server"] = "FastAPI Server"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Type"] = "application/json"
    response.headers["X-RateLimit-Limit"] = str(MAX_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(MAX_REQUESTS - request_count)

    return response


# GET all students (yêu cầu API key)
@app.get("/students", status_code=200)
def get_students(x_api_key: str = Header(None), user_agent: str = Header(None), accept: str = Header("application/json")):
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="Missing API Key")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return {"students": list(students_db.values()), "User-Agent": user_agent, "Accept": accept}


# GET student by ID
@app.get("/students/{student_id}", status_code=200)
def get_student(student_id: int):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    return students_db[student_id]


# POST create student
@app.post("/students", status_code=201)
def create_student(student: Student, x_api_key: str = Header(None)):
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="Missing API Key")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # Check lỗi 400
    if student.age <= 0:
        raise HTTPException(status_code=400, detail="Age must be greater than 0")
    if not student.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    if student.id in students_db:
        raise HTTPException(status_code=403, detail="Student already exists")

    students_db[student.id] = student.dict()
    return {"message": "Student created", "student": student}


# PUT update student (full update)
@app.put("/students/{student_id}", status_code=200)
def update_student(student_id: int, student: Student):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    students_db[student_id] = student.dict()
    return {"message": "Student updated", "student": student}


# PATCH update student (partial update)
@app.patch("/students/{student_id}", status_code=200)
def patch_student(student_id: int, student: dict):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    students_db[student_id].update(student)
    return {"message": "Student partially updated", "student": students_db[student_id]}


# DELETE student
@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    del students_db[student_id]
    return
