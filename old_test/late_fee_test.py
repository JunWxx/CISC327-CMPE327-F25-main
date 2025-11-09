import pytest
from services.library_service import (
    calculate_late_fee_for_book, borrow_book_by_patron
)

from datetime import datetime, timedelta
import database as db


def test_no_overdue():
    now = datetime.now()
    db.insert_borrow_record("123456", 1, now, now + timedelta(days=14))
    db.update_book_availability(1, -1)

    result = calculate_late_fee_for_book("123456", 1)

    assert result["days_overdue"] == 0
    assert result["fee_amount"] == 0.0


def test_overdue_within_7_days():
    now = datetime.now()
    due_date = now - timedelta(days=3)
    borrow_date = due_date - timedelta(days=14)
    db.insert_borrow_record("123456", 1, borrow_date, due_date)
    db.update_book_availability(1, -1)

    result = calculate_late_fee_for_book("123456", 1)

    assert result["days_overdue"] == 3
    assert result["fee_amount"] == 1.5


def test_overdue_beyond_7_days():
    now = datetime.now()
    due_date = now - timedelta(days=10)
    borrow_date = due_date - timedelta(days=14)
    db.insert_borrow_record("123456", 1, borrow_date, due_date)
    db.update_book_availability(1, -1)

    result = calculate_late_fee_for_book("123456", 1)

    assert result["days_overdue"] == 10
    assert result["fee_amount"] == 6.5


def test_overdue_max_fee():
    now = datetime.now()
    due_date = now - timedelta(days=40)
    borrow_date = due_date - timedelta(days=14)
    db.insert_borrow_record("123456", 1, borrow_date, due_date)
    db.update_book_availability(1, -1)

    result = calculate_late_fee_for_book("123456", 1)

    assert result["days_overdue"] == 40
    assert result["fee_amount"] == 15.0


def test_invalid_patron():
    for bid in [1, 2, 3, 4, 5]:
        db.insert_borrow_record("123456", bid, datetime.now(), datetime.now() + timedelta(days=14))
        db.update_book_availability(bid, -1)

    success, message = borrow_book_by_patron("123456", 1)
    assert success is False


