# tests/test_e2e.py

import time
from playwright.sync_api import Page, expect


BASE_URL = "http://127.0.0.1:5000"   


def test_add_book_flow(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("link", name="Add Book").click()

    # Add book
    suffix = str(int(time.time()))
    title = f"E2E Test Book {suffix}"
    author = "E2E Author"
    isbn = "978" + suffix[-10:]
    copies = "3"

    # Input
    page.get_by_label("Title").fill(title)
    page.get_by_label("Author").fill(author)
    page.get_by_label("ISBN").fill(isbn)
    page.get_by_label("Total Copies").fill(copies)

    # Add Book to Catalog
    page.get_by_role("button", name="Add Book to Catalog").click()
    page.get_by_role("link", name="Catalog").click()

    # Assert
    expect(page.get_by_role("cell", name=title)).to_be_visible()
    expect(page.get_by_role("cell", name=isbn)).to_be_visible()

def test_borrow_book_flow(page: Page):
    page.goto(BASE_URL)

    # Add a book for testing
    page.get_by_role("link", name="Add Book").click()

    suffix = str(int(time.time()))
    title = f"E2E Borrow Book {suffix}"
    author = "Borrow Author"
    isbn = "978" + suffix[-10:]   
    copies = "1"                  

    page.get_by_label("Title").fill(title)
    page.get_by_label("Author").fill(author)
    page.get_by_label("ISBN").fill(isbn)
    page.get_by_label("Total Copies").fill(copies)
    page.get_by_role("button", name="Add Book to Catalog").click()

    page.get_by_role("link", name="Catalog").click()

    # Find the book in the table
    book_row = page.get_by_role("row", name=title)
    expect(book_row.get_by_text("Available")).to_be_visible()

    # Input Patron ID and Borrow 
    book_row.get_by_placeholder("Patron ID").fill("123456")
    book_row.get_by_role("button", name="Borrow").click()
    book_row_new = page.get_by_role("row", name=title)

    # Assert
    expect(book_row_new.get_by_text("Not Available")).to_be_visible()

