# book_service/tests/test_book_service.py

import pytest
from unittest.mock import MagicMock, call

# Import Service và các Exceptions
from src.services.book_service import BookService
from src.repositories.book_repository import BookRepository
from src.models.book_model import Book # Cần import để mock
from src.exceptions import (
    BookNotFoundError, BookAlreadyExistsError, 
    InvalidBookDataError, NotEnoughCopiesError
)

# --- FIXTURES ---

@pytest.fixture
def mock_repo(mocker):
    """Tạo một BookRepository giả mạo (mock)"""
    # spec=True đảm bảo mock này có các hàm giống hệt class thật
    return mocker.Mock(spec=BookRepository)

@pytest.fixture
def book_service(mock_repo):
    """Tạo một BookService và "tiêm" (inject) mock_repo vào"""
    service = BookService()
    service.repo = mock_repo
    return service

# --- TEST CRUD ---

# Test hàm create_book
def test_create_book_success(book_service, mock_repo):
    """Test Happy Path: Tạo sách thành công"""
    data = {"title": "Lão Hạc", "author": "Nam Cao", "available_copies": 10}
    
    # Setup: Repo nói rằng sách này CHƯA tồn tại
    mock_repo.find_by_title_and_author.return_value = None
    
    # Action
    book_service.create_book(data)
    
    # Assert
    # Kiểm tra xem repo được gọi đúng
    mock_repo.find_by_title_and_author.assert_called_with("Lão Hạc", "Nam Cao")
    # Kiểm tra xem repo.save đã được gọi với một object Book
    mock_repo.save.assert_called_once()
    saved_book = mock_repo.save.call_args[0][0] # Lấy tham số đầu tiên
    assert isinstance(saved_book, Book)
    assert saved_book.title == "Lão Hạc"

def test_create_book_raises_invalid_data(book_service):
    """Test Sad Path: Tạo sách thiếu tiêu đề"""
    data = {"author": "Nam Cao"} # Thiếu title
    
    with pytest.raises(InvalidBookDataError, match="Title and Author cannot be empty"):
        book_service.create_book(data)

def test_create_book_raises_already_exists(book_service, mock_repo):
    """Test Sad Path: Tạo sách bị trùng"""
    data = {"title": "Lão Hạc", "author": "Nam Cao"}
    
    # Setup: Repo nói sách này ĐÃ tồn tại
    mock_repo.find_by_title_and_author.return_value = MagicMock(spec=Book)
    
    with pytest.raises(BookAlreadyExistsError):
        book_service.create_book(data)

# Test hàm get_book_by_id
def test_get_book_by_id_raises_not_found(book_service, mock_repo):
    """Test Sad Path: Lấy sách không tồn tại"""
    # Setup: Repo trả về None
    mock_repo.get_by_id.return_value = None
    
    with pytest.raises(BookNotFoundError):
        book_service.get_book_by_id(999)

# Test hàm check_and_update_copies
def test_update_copies_success_borrow(book_service, mock_repo):
    """Test Happy Path: Mượn sách thành công"""
    # Setup: Tạo một mock book thật
    mock_book = Book(id=1, title="Test", author="Test", available_copies=5)
    mock_repo.get_by_id.return_value = mock_book
    
    # Action
    new_copies = book_service.check_and_update_copies(1, 2, 'borrow')
    
    # Assert
    assert new_copies == 3
    assert mock_book.available_copies == 3 # Kiểm tra object đã bị thay đổi
    mock_repo.save.assert_called_with(mock_book) # Kiểm tra repo đã lưu

def test_update_copies_raises_not_enough(book_service, mock_repo):
    """Test Sad Path: Mượn sách không đủ số lượng"""
    mock_book = Book(id=1, title="Test", author="Test", available_copies=5)
    mock_repo.get_by_id.return_value = mock_book
    
    with pytest.raises(NotEnoughCopiesError):
        book_service.check_and_update_copies(1, 6, 'borrow') # Mượn 6 trong khi có 5
        
    mock_repo.save.assert_not_called() # Không được lưu

def test_update_copies_raises_book_not_found(book_service, mock_repo):
    """Test Sad Path: Cập nhật sách không tồn tại"""
    mock_repo.get_by_id.return_value = None
    
    with pytest.raises(BookNotFoundError):
        book_service.check_and_update_copies(999, 1, 'borrow')