import pytest
from library_service import (
    borrow_book_by_patron
)

def test_borrow_valid_input():
    success, message = borrow_book_by_patron("123456", 1)

    assert success == True
    assert "successfully borrowed" in message.lower()


def test_borrow_invalid_patron_id():
    success, message = borrow_book_by_patron("12345a", 1)

    assert success == False
    assert "6 digit" in message


def test_borrow_book_unavailable():
    success, message = borrow_book_by_patron("123456", 100) #100 doesn't exist

    assert success == False
    assert "The book is unavailable" in message.lower()


def test_borrow_over_limit():
    """Test when patron already has 5 books."""
    success, message = borrow_book_by_patron("123456", 1)

    assert success == False
    assert "limited" in message.lower()