import pytest
from library_service import (
    return_book_by_patron
)


def test_return_valid_input():
    success, message = return_book_by_patron("123456", 1)

    assert success == True
    assert "successfully returned" in message.lower()


def test_return_invalid_patron_id():
    success, message = return_book_by_patron("12345a", 1)

    assert success == False
    assert "6 digit" in message


def test_return_not_borrowed_by_patron():
    success, message = return_book_by_patron("123456", 100)  #100 is not borrowed
    assert success == False
    assert "not borrowed" in message.lower()


def test_return_invalid_book_id():
    success, message = return_book_by_patron("123456", -1)

    assert success == False
    assert "invalid ID" in message.lower()
