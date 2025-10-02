import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional
import uvicorn
# ----------------------------------------------------------------------
# 1. DATABASE ẢO - SỬ DỤNG MÔ HÌNH 3 BẢNG CHUẨN HÓA
# ----------------------------------------------------------------------

# Bảng 1: Student (Thông tin tĩnh)
STUDENTS_DB = {
    1: {"id": 1, "name": "Bùi Anh Chiến"},
    2: {"id": 2, "name": "Nguyễn Mạnh Quỳnh"},
    3: {"id": 3, "name": "Nguyễn Duy Đức"},
}

# Bảng 2: Subject_Score (Điểm môn học)
# student_id là khóa ngoại
SUBJECT_SCORES_DB = [
    {"student_id": 1, "subject": "Math", "score": 9.0},
    {"student_id": 1, "subject": "Lit", "score": 8.5},
    {"student_id": 1, "subject": "Eng", "score": 9.5},
    {"student_id": 2, "subject": "Math", "score": 6.0},
    {"student_id": 2, "subject": "Lit", "score": 5.5},
    {"student_id": 2, "subject": "Eng", "score": 7.0},
    {"student_id": 3, "subject": "Math", "score": 4.0},
    {"student_id": 3, "subject": "Lit", "score": 5.0},
    {"student_id": 3, "subject": "Eng", "score": 4.5},
]

# Bảng 3: Conduct_Score (Điểm Rèn Luyện)
# student_id là khóa ngoại
CONDUCT_SCORES_DB = {
    1: {"rl_score": 95},
    2: {"rl_score": 70},
    3: {"rl_score": 50},
}

# ----------------------------------------------------------------------
# 2. LOGIC NGHIỆP VỤ (SERVICE LAYER)
# ----------------------------------------------------------------------

def get_student_scores(student_id: int) -> List[float]:
    """Lấy danh sách điểm môn học từ bảng SUBJECT_SCORES_DB."""
    return [item["score"] for item in SUBJECT_SCORES_DB if item["student_id"] == student_id]

def get_rl_score(student_id: int) -> int:
    """Lấy điểm rèn luyện từ bảng CONDUCT_SCORES_DB."""
    return CONDUCT_SCORES_DB.get(student_id, {}).get("rl_score", 0)

def calc_avg_and_grade(scores: List[float]) -> tuple[Optional[float], str]:
    """Tính điểm TB và học lực."""
    if not scores:
        return None, "Chưa có điểm"
    avg = sum(scores) / len(scores)
    # Giữ nguyên logic đánh giá điểm TB
    if avg >= 9: grade = "Xuất sắc"
    elif avg >= 8: grade = "Giỏi"
    elif avg >= 7: grade = "Khá"
    elif avg >= 5: grade = "Trung bình"
    else: grade = "Yếu"
    return avg, grade

def calc_title(avg: Optional[float], rl_score: int) -> str:
    """Tính danh hiệu dựa trên học lực + rèn luyện."""
    if avg is None:
        return "Chưa có danh hiệu"
    # Giữ nguyên logic đánh giá danh hiệu
    if avg >= 9 and rl_score >= 90:
        return "Học sinh Xuất sắc"
    elif avg >= 8 and rl_score >= 80:
        return "Học sinh Giỏi"
    elif avg >= 7 and rl_score >= 65:
        return "Học sinh Khá"
    elif avg >= 5 and rl_score >= 50:
        return "Học sinh Trung bình"
    else:
        return "Không đạt danh hiệu"

# ----------------------------------------------------------------------
# 3. ĐỊNH NGHĨA GRAPHQL SCHEMA MỚI
# ----------------------------------------------------------------------

@strawberry.type
class Student:
    id: int
    name: str

    @strawberry.field
    def average(self) -> Optional[float]:
        # Truy vấn Service Layer để lấy điểm từ bảng SUBJECT_SCORES_DB
        scores = get_student_scores(self.id)
        avg, _ = calc_avg_and_grade(scores)
        return avg

    @strawberry.field
    def grade(self) -> str:
        # Truy vấn Service Layer
        scores = get_student_scores(self.id)
        _, grade = calc_avg_and_grade(scores)
        return grade

    @strawberry.field
    def rl_score(self) -> int:
        # Truy vấn Service Layer để lấy điểm từ bảng CONDUCT_SCORES_DB
        return get_rl_score(self.id)

    @strawberry.field
    def title(self) -> str:
        # Truy vấn Service Layer và áp dụng Logic Nghiệp vụ
        scores = get_student_scores(self.id)
        avg, _ = calc_avg_and_grade(scores)
        rl_score = get_rl_score(self.id)
        return calc_title(avg, rl_score)

@strawberry.type
class Query:
    @strawberry.field
    def student(self, id: int) -> Optional[Student]:
        # Truy vấn bảng STUDENTS_DB
        data = STUDENTS_DB.get(id)
        if not data:
            return None
        return Student(id=data["id"], name=data["name"])

    @strawberry.field
    def all_students(self) -> List[Student]:
        # Lấy danh sách từ bảng STUDENTS_DB
        return [Student(id=data["id"], name=data["name"]) for data in STUDENTS_DB.values()]

schema = strawberry.Schema(query=Query)

# ----------------------------------------------------------------------
# 4. KHỞI TẠO FASTAPI
# ----------------------------------------------------------------------

app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=5000)

# Run: uvicorn [ten_file]:app --reload --port 5000