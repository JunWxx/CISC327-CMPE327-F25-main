import pytest
from library_service import (
    calculate_late_fee_for_book
)


def test_no_overdue():
    success, result = calculate_late_fee_for_book("123456", 1)

    assert success == True
    assert result["days_overdue"] == 0
    assert result["fee"] == 0.0


def test_overdue_within_7_days():
    success, result = calculate_late_fee_for_book("123456", 1)

    assert success == True
    assert result["days_overdue"] == 3
    assert result["fee"] == 1.5


def test_overdue_beyond_7_days():
    success, result = calculate_late_fee_for_book("123456", 1)

    assert success == True
    assert result["days_overdue"] == 10
    assert result["fee"] == 6.5


def test_overdue_max_fee():
    success, result = calculate_late_fee_for_book("123456", 1)

    assert success == True
    assert result["days_overdue"] == 40
    assert result["fee"] == 15.0


def test_invalid_patron():
    success, message = calculate_late_fee_for_book("12345a", 1)

    assert success == False
    assert "limited" in message.lower()
