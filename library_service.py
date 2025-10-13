"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    
    TODO: Implement R4 as per requirements
    """
    #1. Validate Partion_ID 
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    #2. Verifies the book was borrowed by the patron
    borrowed_books = get_patron_borrowed_books(patron_id)
    borrowed_book_ids = [b['book_id'] for b in borrowed_books]

    if book_id not in borrowed_book_ids:
        return False, "This book was not borrowed by this patron or already returned."
    
    #3. Update return record and availability
    now = datetime.now()
    success_return = update_borrow_record_return_date(patron_id, book_id, now)
    success_avail = update_book_availability(book_id, +1)

    if not success_return or not success_avail:
        return False
    
    #4. Calculate late fee
    fee_info = calculate_late_fee_for_book(patron_id, book_id)
    if fee_info['fee_amount'] > 0:
        return True, f'Book returned successfully. Late fee: fee_info["fee_amount"].'
    else:
        return True, "Book returned successfully. No late fee owed."
    

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    
    TODO: Implement R5 as per requirements 
    
    
    return { // return the calculated values
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Late fee calculation not implemented'
    }
    """
    result = {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'No fee'}

    #1. Get book info
    borrowed_books = get_patron_borrowed_books(patron_id)

    record = None
    for b in borrowed_books:
        if b['book_id'] == book_id:
            record = b
            break

    if not record:
        result['status'] = 'No active borrow record'
        return result

    due_date = record['due_date']
    now = datetime.now()

    if now <= due_date:
        return result  # 

    #2. Calculate overdue days
    days_overdue = (now - due_date).days
    result['days_overdue'] = days_overdue

    #3. Calculate fee
    if days_overdue <= 7:
        fee = days_overdue * 0.5
    else:
        fee = 7 * 0.5 + (days_overdue - 7) * 1.0

    result['fee_amount'] = min(fee, 15.00)
    if result['fee_amount'] > 0:
        result['status'] = 'Overdue'
    else:
        result['status'] = 'No fee'

    return result


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """
    
    if not search_term :
        return []

    search_term = search_term.lower()
    books = get_all_books()  

    results = []
    for book in books:
        if search_type == 'title' and search_term in book['title'].lower():
            results.append(book)
        elif search_type == 'author' and search_term in book['author'].lower():
            results.append(book)
        elif search_type == 'isbn' and search_term == book['isbn']:
            results.append(book)

    return results

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    TODO: Implement R7 as per requirements
    """
    # Verify id
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {"error": "Invalid patron ID."}

    # Current borrowing status
    borrowed_books = get_patron_borrowed_books(patron_id)
    borrow_count = get_patron_borrow_count(patron_id)

    # Late fee
    total_fees = 0.0
    for book in borrowed_books:
        fee_info = calculate_late_fee_for_book(patron_id, book['book_id'])
        total_fees += fee_info['fee_amount']

    # report
    report = {
        "patron_id": patron_id,
        "borrow_count": borrow_count,
        "currently_borrowed": borrowed_books,
        "total_late_fees": round(total_fees, 2)
    }

    return report
