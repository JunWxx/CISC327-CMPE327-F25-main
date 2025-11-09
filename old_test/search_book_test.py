import pytest
from services.library_service import (
    search_books_in_catalog
)


def test_search_title_partial_match():
    results = search_books_in_catalog("Great", "title")

    assert any(b.get("title") == "The Great Gatsby" for b in results)


def test_search_author_partial_match():
    results = search_books_in_catalog("Lee", "author")

    assert any(b.get("title") == "To Kill a Mockingbird" for b in results)


def test_search_isbn_exact_match():
    results = search_books_in_catalog("9780743273565", "isbn")

    assert any(b.get("title") == "The Great Gatsby" for b in results)


def test_search_isbn_wrong_length():
    results = search_books_in_catalog("12345", "isbn")

    assert results == []


def test_search_no_results():
    results = search_books_in_catalog("ABCDE", "title")

    assert results == []
