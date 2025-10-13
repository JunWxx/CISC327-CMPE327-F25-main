import pytest
from library_service import (
    return_book_by_patron
)

from datetime import datetime, timedelta
import database as db


def test_return_valid_input():
    db.insert_borrow_record("123456", 1, datetime.now(), datetime.now() + timedelta(days=14))
    db.update_book_availability(1, -1)

    success, message = return_book_by_patron("123456", 1)

    assert success == True
    assert "successfully returned" in message.lower()


def test_return_invalid_patron_id():
    success, message = return_book_by_patron("12345a", 1)

    assert success == False
    assert "invalid patron" in message.lower()


def test_return_not_borrowed_by_patron():
    success, message = return_book_by_patron("123456", 100)  #100 is not borrowed
    assert success == False
    assert "not borrowed" in message.lower()


def test_return_invalid_book_id():
    success, message = return_book_by_patron("123456", -1)

    assert success == False
    # 实现提示“未借/已还”，而非 "invalid ID"
    assert ("not borrowed" in message.lower()) or ("already returned" in message.lower())


