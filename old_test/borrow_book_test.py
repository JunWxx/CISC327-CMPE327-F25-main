import pytest
from services.library_service import borrow_book_by_patron

from datetime import datetime, timedelta
import database as db


def test_borrow_valid_input():
    success, message = borrow_book_by_patron("123456", 1)
    
    assert success == True
    assert "successfully borrowed" in message.lower()

def test_borrow_book_unavailable():
    success, message = borrow_book_by_patron("123456", 100) #100 doesn't exist

    assert success == False
    assert "not found" in message.lower()


def test_borrow_over_limit():
    """Test when patron already has 5 books."""
    for bid in [1, 2, 3, 4, 5]:
        db.insert_borrow_record("123456", bid, datetime.now(), datetime.now() + timedelta(days=14))
        db.update_book_availability(bid, -1)

    success, message = borrow_book_by_patron("123456", 1)

    assert success == False
