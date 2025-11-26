import pytest
from unittest.mock import MagicMock, call

# Import Service, Repo, Model, và Exceptions
from src.services.book_service import BookService
from src.repositories.book_repository import BookRepository
from src.models.book_model import Book
from src.exceptions import (
    BookNotFoundError, BookAlreadyExistsError, 
    InvalidBookDataError, NotEnoughCopiesError
)

# --- FIXTURES ---

@pytest.fixture
def mock_repo(mocker):
    """Tạo một BookRepository giả mạo (mock)"""
    
    # DÒNG CŨ: return mocker.Mock(spec=BookRepository)
    
    # ✅ DÒNG MỚI:
    # 1. Vẫn tạo mock nghiêm ngặt
    mock = mocker.Mock(spec=BookRepository)
    
    # 2. "Dạy" cho mock biết về hàm mới (để service có thể gọi)
    #    ngay cả khi hàm này chưa tồn tại trong file .py của repo thật.
    mock.update_copies_atomically = mocker.Mock()
    
    return mock

@pytest.fixture
def book_service(mock_repo):
    """Tạo một BookService và "tiêm" (inject) mock_repo vào"""
    service = BookService()
    service.repo = mock_repo
    return service

@pytest.fixture
def mock_book():
    """Tạo một đối tượng Book giả để tái sử dụng"""
    book = MagicMock(spec=Book)
    book.id = 1
    book.title = "Lão Hạc"
    book.author = "Nam Cao"
    book.available_copies = 5
    book.to_dict.return_value = {
        "id": 1, "title": "Lão Hạc", "author": "Nam Cao", "available_copies": 5
    }
    return book

# ====================================================================
# TEST HÀM: create_book (PASS)
# ====================================================================

def test_create_book_success(book_service, mock_repo):
    data = {"title": "Lão Hạc", "author": "Nam Cao", "available_copies": 10}
    mock_repo.find_by_title_and_author.return_value = None
    
    book_service.create_book(data)
    
    mock_repo.find_by_title_and_author.assert_called_with("Lão Hạc", "Nam Cao")
    mock_repo.save.assert_called_once()
    saved_book = mock_repo.save.call_args[0][0]
    assert isinstance(saved_book, Book)
    assert saved_book.title == "Lão Hạc"
    assert saved_book.available_copies == 10

def test_create_book_handles_default_copies(book_service, mock_repo):
    data = {"title": "Sách Mới", "author": "Tác Giả"}
    mock_repo.find_by_title_and_author.return_value = None
    
    book_service.create_book(data)
    
    mock_repo.save.assert_called_once()
    saved_book = mock_repo.save.call_args[0][0]
    assert saved_book.available_copies == 0

def test_create_book_raises_invalid_data(book_service):
    data = {"author": "Nam Cao"}
    
    with pytest.raises(InvalidBookDataError, match="Title and Author cannot be empty"):
        book_service.create_book(data)

def test_create_book_raises_already_exists(book_service, mock_repo):
    data = {"title": "Lão Hạc", "author": "Nam Cao"}
    mock_repo.find_by_title_and_author.return_value = MagicMock(spec=Book)
    
    with pytest.raises(BookAlreadyExistsError):
        book_service.create_book(data)

# ====================================================================
# TEST HÀM: get_book_by_id (PASS)
# ====================================================================

def test_get_book_by_id_success(book_service, mock_repo, mock_book, mocker):
    mock_repo.get_by_id.return_value = mock_book
    mocker.patch.object(book_service, 'add_hateoas_book', lambda x, y: x) 

    result = book_service.get_book_by_id(1, base_url="test_url")
    
    mock_repo.get_by_id.assert_called_with(1)
    assert result is not None
    assert result['id'] == 1

def test_get_book_by_id_raises_not_found(book_service, mock_repo):
    mock_repo.get_by_id.return_value = None
    
    with pytest.raises(BookNotFoundError):
        book_service.get_book_by_id(999)

# ====================================================================
# TEST HÀM: update_book (PASS)
# ====================================================================

def test_update_book_success(book_service, mock_repo, mock_book):
    mock_repo.get_by_id.return_value = mock_book
    update_data = {
        "title": "Chí Phèo",
        "available_copies": 2
    }
    
    book_service.update_book(1, update_data)
    
    assert mock_book.title == "Chí Phèo"
    assert mock_book.author == "Nam Cao"
    assert mock_book.available_copies == 2
    mock_repo.save.assert_called_with(mock_book)

def test_update_book_raises_not_found(book_service, mock_repo):
    mock_repo.get_by_id.return_value = None
    
    with pytest.raises(BookNotFoundError):
        book_service.update_book(999, {"title": "Test"})
    
    mock_repo.save.assert_not_called()

def test_update_book_raises_invalid_data(book_service, mock_repo, mock_book):
    mock_repo.get_by_id.return_value = mock_book
    invalid_data = {"title": ""}
    
    with pytest.raises(InvalidBookDataError, match="Title and Author cannot be empty"):
        book_service.update_book(1, invalid_data)
        
    mock_repo.save.assert_not_called()

# ====================================================================
# TEST HÀM: delete_book (PASS)
# ====================================================================

def test_delete_book_success(book_service, mock_repo, mock_book):
    mock_repo.get_by_id.return_value = mock_book
    
    book_service.delete_book(1)
    
    mock_repo.get_by_id.assert_called_with(1)
    mock_repo.delete.assert_called_with(mock_book)

def test_delete_book_raises_not_found(book_service, mock_repo):
    mock_repo.get_by_id.return_value = None
    
    with pytest.raises(BookNotFoundError):
        book_service.delete_book(999)
        
    mock_repo.delete.assert_not_called()

# ====================================================================
# TEST HÀM: check_and_update_copies (ĐÃ SỬA LỖI)
# ====================================================================

def test_update_copies_success_borrow(book_service, mock_repo, mock_book):
    """Test Happy Path: Mượn sách thành công"""
    mock_book.available_copies = 3
    mock_repo.update_copies_atomically.return_value = mock_book
    
    new_copies = book_service.check_and_update_copies(1, 2, 'borrow')
    
    assert new_copies == 3
    mock_repo.update_copies_atomically.assert_called_with(1, -2)

def test_update_copies_success_return(book_service, mock_repo, mock_book):
    """Test Happy Path: Trả sách thành công"""
    mock_book.available_copies = 8
    mock_repo.update_copies_atomically.return_value = mock_book
    
    new_copies = book_service.check_and_update_copies(1, 3, 'return')
    
    assert new_copies == 8
    mock_repo.update_copies_atomically.assert_called_with(1, 3)

def test_update_copies_raises_not_enough(book_service, mock_repo):
    """Test Sad Path: Mượn sách không đủ (Repo ném lỗi)"""
    mock_repo.update_copies_atomically.side_effect = Exception("check constraint")
    
    with pytest.raises(NotEnoughCopiesError):
        book_service.check_and_update_copies(1, 6, 'borrow')

def test_update_copies_raises_book_not_found(book_service, mock_repo):
    """Test Sad Path: Sách không tồn tại (Repo ném lỗi)"""
    mock_repo.update_copies_atomically.side_effect = Exception("Not found")
    
    with pytest.raises(BookNotFoundError):
        book_service.check_and_update_copies(999, 1, 'borrow')

def test_update_copies_raises_invalid_quantity(book_service, mock_repo):
    """Test Sad Path: Số lượng không hợp lệ"""
    with pytest.raises(InvalidBookDataError, match="Quantity must be positive"):
        book_service.check_and_update_copies(1, 0, 'borrow')
        
    with pytest.raises(InvalidBookDataError, match="Quantity must be positive"):
        book_service.check_and_update_copies(1, -1, 'return')

    mock_repo.update_copies_atomically.assert_not_called()

# ====================================================================
# TEST HÀM: get_books_offset (ĐÃ SỬA LỖI)
# ====================================================================

def test_get_books_offset_happy_path(book_service, mock_repo, mocker):
    """Test Happy Path: Lấy danh sách sách và kiểm tra cấu trúc phân trang"""
    # Setup
    mock_book_1 = MagicMock(spec=Book); mock_book_1.to_dict.return_value = {"id": 1, "title": "Sách 1"}
    mock_book_2 = MagicMock(spec=Book); mock_book_2.to_dict.return_value = {"id": 2, "title": "Sách 2"}
    
    mock_repo.get_total_count.return_value = 10
    mock_repo.get_all_offset.return_value = [mock_book_1, mock_book_2]
    
    mocker.patch.object(book_service, 'add_hateoas_book', lambda x, y: x)
    mocker.patch.object(book_service, 'paginate_links', lambda *args, **kwargs: {"test": "link"})

    # Action: Lấy trang 1, 2 cuốn sách
    result = book_service.get_books_offset(page=1, limit=2, base_url="test")
    
    # Assert
    mock_repo.get_all_offset.assert_called_with(0, 2, None)
    
    assert result["metadata"]["total_records"] == 10
    assert result["metadata"]["page"] == 1
    assert result["metadata"]["total_pages"] == 5
    assert len(result["data"]) == 2
    assert result["data"][0]["title"] == "Sách 1"
    assert result["links"]["test"] == "link"

def test_get_books_offset_with_filter(book_service, mock_repo, mocker):
    """Test Edge Case: Lấy sách có filter"""
    mock_repo.get_total_count.return_value = 1
    mock_repo.get_all_offset.return_value = []
    mocker.patch.object(book_service, 'add_hateoas_book', lambda x, y: x)
    mocker.patch.object(book_service, 'paginate_links', lambda *args, **kwargs: {})

    # Action
    book_service.get_books_offset(page=1, limit=5, author_filter="Nam Cao", base_url="test")
    
    # Assert
    mock_repo.get_total_count.assert_called_with("Nam Cao")
    
    # DÒNG CŨ: mock_repo.get_all_offset.assert_called_with(offset=0, limit=5, author_filter="Nam Cao")
    # ✅ DÒNG MỚI: Sửa lại để khớp với cách gọi (positional args)
    mock_repo.get_all_offset.assert_called_with(0, 5, "Nam Cao")

def test_get_books_offset_empty_result(book_service, mock_repo, mocker):
    """Test Edge Case: Không có sách nào (trang 1)"""
    mock_repo.get_total_count.return_value = 0
    mock_repo.get_all_offset.return_value = []
    mocker.patch.object(book_service, 'add_hateoas_book', lambda x, y: x)
    mocker.patch.object(book_service, 'paginate_links', lambda *args, **kwargs: {})

    # Action
    result = book_service.get_books_offset(page=1, limit=5, base_url="test")

    # Assert
    assert result["metadata"]["total_records"] == 0
    assert result["metadata"]["total_pages"] == 0
    assert len(result["data"]) == 0