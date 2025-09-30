from fastapi import APIRouter, FastAPI
from typing import List, Dict, Any, Optional

app = FastAPI(
    title="Student Performance API (Layered Demo)",
    description="Ứng dụng quản lý hiệu suất sinh viên.",
    version="1.0.0"
)

# Khởi tạo APIRouter. Router này sẽ quản lý tất cả các endpoint liên quan đến sinh viên.
router = APIRouter(
    prefix="/students", # Đặt tiền tố cho tất cả các endpoint trong router này
    tags=["Students Performance"],
)

app.include_router(router)
# ----------------------------------------------------------------------
# 1. DATABASE ẢO - DATA ACCESS LAYER (DAL)
# ----------------------------------------------------------------------

STUDENTS_DB = {
    1: {"id": 1, "name": "Bùi Anh Chiến"},
    2: {"id": 2, "name": "Nguyễn Mạnh Quỳnh"},
    3: {"id": 3, "name": "Nguyễn Duy Đức"},
}
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
CONDUCT_SCORES_DB = {
    1: {"rl_score": 95},
    2: {"rl_score": 70},
    3: {"rl_score": 50},
}

# Hàm truy cập dữ liệu (DAL/Repository)
def get_student_scores(student_id: int) -> List[float]:
    """DAL: Lấy danh sách điểm môn học từ bảng SUBJECT_SCORES_DB."""
    return [item["score"] for item in SUBJECT_SCORES_DB if item["student_id"] == student_id]

def get_rl_score(student_id: int) -> int:
    """DAL: Lấy điểm rèn luyện từ bảng CONDUCT_SCORES_DB."""
    return CONDUCT_SCORES_DB.get(student_id, {}).get("rl_score", 0)

# ----------------------------------------------------------------------
# 2. LOGIC NGHIỆP VỤ (SERVICE LAYER)
# ----------------------------------------------------------------------

def calc_avg_and_grade(scores: List[float]) -> tuple[Optional[float], str]:
    """Service: Tính điểm TB (AVG)."""
    if not scores:
        return None, "Chưa có điểm"
    avg = sum(scores) / len(scores)
    return avg, ""

def get_evaluation_title(avg: Optional[float], rl_score: int) -> str:
    """Service: Áp dụng logic nghiệp vụ để tính Đánh giá/Danh hiệu."""
    if avg is None:
        return "Chưa có danh hiệu"
    
    if avg >= 9 and rl_score >= 90:
        return "Xuất sắc"
    elif avg >= 8 and rl_score >= 80:
        return "Giỏi"
    elif avg >= 7 and rl_score >= 65:
        return "Khá"
    elif avg >= 5 and rl_score >= 50:
        return "Trung bình"
    else:
        return "Yếu/Không đạt"
    
def calculate_student_performance(student_id: int) -> Optional[Dict[str, Any]]:
    """Service: Hàm tổng hợp, tính toán tất cả thông số."""
    student_data = STUDENTS_DB.get(student_id)
    if not student_data:
        return None

    scores = get_student_scores(student_id)
    gpa, _ = calc_avg_and_grade(scores)
    rl_score = get_rl_score(student_id)
    evaluation = get_evaluation_title(gpa, rl_score)
    
    return {
        "id": student_id,
        "name": student_data["name"],
        "gpa": round(gpa, 2) if gpa is not None else None,
        "rl_score": rl_score,
        "evaluation": evaluation
    }

# ----------------------------------------------------------------------
# 3. API CONTROLLER (ENDPOINT)
# ----------------------------------------------------------------------

@router.get(
    "/performance_summary", 
    response_model=List[Dict[str, Any]],
    summary="Lấy tổng hợp hiệu suất của tất cả sinh viên"
)
def get_all_students_performance():
    """
    Controller: Endpoint RESTful trả về danh sách sinh viên kèm ĐTB, ĐRL, và Đánh giá.
    Đường dẫn đầy đủ sẽ là /students/performance_summary
    """
    performance_list = []
    
    # Lặp qua tất cả sinh viên và gọi hàm Service
    for student_id in STUDENTS_DB.keys():
        data = calculate_student_performance(student_id)
        if data:
            performance_list.append(data)
            
    return performance_list
# uvicorn RESTful.Server:router --reload --port 8000