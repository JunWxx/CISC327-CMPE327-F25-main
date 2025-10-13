import pytest
from library_service import (
    get_patron_status_report
)


def test_patron_status_valid():
    success, message = get_patron_status_report("123456")

    assert success is True
    assert "borrowed" in message.lower()
    assert "due" in message.lower()
    assert "late fee" in message.lower()
    assert "history" in message.lower()


def test_patron_status_no_borrows():
    success, message = get_patron_status_report("654321")

    assert success is True
    assert "0" in message
    assert "borrowed" in message.lower()
    assert "late fee" in message.lower()


def test_patron_status_invalid_patron_id():
    success, message = get_patron_status_report("12A45A")

    assert success is False
    assert "6-digit" in message
