# book_service/src/exceptions.py

class BookServiceError(Exception):
    """Lỗi cơ sở cho tất cả các lỗi trong service này"""
    pass

class BookNotFoundError(BookServiceError):
    """Ném ra khi không tìm thấy sách (ID không tồn tại)"""
    pass

class BookAlreadyExistsError(BookServiceError):
    """Ném ra khi tạo một sách đã tồn tại (trùng title và author)"""
    pass

class InvalidBookDataError(BookServiceError):
    """Ném ra khi dữ liệu đầu vào vi phạm logic (ví dụ: title rỗng)"""
    pass

class NotEnoughCopiesError(BookServiceError):
    """Ném ra khi mượn sách nhưng không đủ số lượng"""
    pass