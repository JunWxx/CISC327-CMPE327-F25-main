import pytest
from library_service import (
    search_books_in_catalog
)


def test_search_title_partial_match():
    success, message = search_books_in_catalog("Great", "title")

    assert success == True
    assert "The Great Gatsby" in message


def test_search_author_partial_match():
    success, message = search_books_in_catalog("Lee", "author")

    assert success == True
    assert "To Kill a Mockingbird" in message


def test_search_isbn_exact_match():
    success, message = search_books_in_catalog("9780743273565", "isbn")

    assert success == True
    assert "The Great Gatsby" in message


def test_search_isbn_wrong_length():
    success, results = search_books_in_catalog("12345", "isbn")

    assert success == False
    assert "13 digits" in results


def test_search_no_results():
    success, results = search_books_in_catalog("ABCDE", "title")

    assert success == True
    assert results == []
