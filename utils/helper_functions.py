# utils/helper_functions.py
"""
Helper Functions
General utilities used across the application.
"""

import re
from datetime import datetime


def validate_email(email):
    """
    Basic email validation using regex.
    
    Parameters:
    email (str): Email address to validate.
    
    Returns:
    bool: True if valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_input(text):
    """
    Remove potentially dangerous characters from user input.
    (Basic XSS prevention)
    
    Parameters:
    text (str): Input string.
    
    Returns:
    str: Sanitized string.
    """
    if not text:
        return ''
    # Remove HTML tags and special characters
    import html
    return html.escape(text.strip())


def format_date(date_obj, format_str='%Y-%m-%d'):
    """
    Format a date object into a string.
    
    Parameters:
    date_obj (datetime.date or None): Date to format.
    format_str (str): Desired format.
    
    Returns:
    str: Formatted date or empty string.
    """
    if date_obj:
        return date_obj.strftime(format_str)
    return ''


def calculate_experience_years(joining_date):
    """
    Calculate years of experience based on joining date.
    
    Parameters:
    joining_date (datetime.date): Date the employee joined.
    
    Returns:
    float: Years of experience (rounded to 1 decimal).
    """
    if not joining_date:
        return 0
    today = datetime.now().date()
    delta = today - joining_date
    years = delta.days / 365.25
    return round(years, 1)


def paginate(query, page, per_page=10):
    """
    Manual pagination helper (if using raw SQL). 
    Flask-SQLAlchemy's paginate() is preferred, but this is a fallback.
    
    Parameters:
    query (SQLAlchemy query): Query object.
    page (int): Page number (1-indexed).
    per_page (int): Items per page.
    
    Returns:
    dict: Contains items, total, page, pages, etc.
    """
    total = query.count()
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    pages = (total + per_page - 1) // per_page
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pages,
        'has_prev': page > 1,
        'has_next': page < pages,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page < pages else None
    }


def generate_employee_code(department_code, joining_year, sequence):
    """
    Generate a unique employee code.
    Example: ENG2024001
    
    Parameters:
    department_code (str): 3-letter dept code (e.g., ENG, HR).
    joining_year (int): Year of joining.
    sequence (int): Incremental number.
    
    Returns:
    str: Employee code.
    """
    return f"{department_code.upper()}{joining_year}{sequence:04d}"


def is_admin(user):
    """Check if user is admin."""
    return user.is_authenticated and user.role == 'admin'


def flash_errors(form, flash_func):
    """
    Flash form validation errors.
    
    Parameters:
    form (FlaskForm): The WTForm instance.
    flash_func (function): Flask's flash function.
    """
    for field, errors in form.errors.items():
        for error in errors:
            flash_func(f"{getattr(form, field).label.text}: {error}", 'danger')