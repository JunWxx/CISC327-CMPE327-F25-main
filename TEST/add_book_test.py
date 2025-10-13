import pytest
from library_service import (
    add_book_to_catalog
)


def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)

    assert success == True
    assert "successfully added" in message.lower()


def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)

    assert success == False
    assert "13 digits" in message

def test_add_book_invalid_isbn_too_long():
    success, message = add_book_to_catalog("Test Book", "Test Author", "12345678901234", 5)

    assert success == False
    assert "13 digits" in message

def test_add_book_invalid_isbn():

    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789012a", 5)

    assert success == False
    assert "It should be 13 digits" in message

def test_add_book_invalid_copies():

    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 0)

    assert success == False
    assert "Copies should be positive" in message