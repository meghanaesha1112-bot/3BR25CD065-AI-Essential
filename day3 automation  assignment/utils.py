import re
from datetime import datetime

def validate_phone(phone: str) -> bool:
    """Validate phone number format (at least 7 digits, allows +, -, spaces, parens)."""
    if not phone or not isinstance(phone, str):
        return False
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 7

def validate_email(email: str) -> bool:
    """Validate basic email format. Empty string is allowed if optional."""
    if not email:
        return True
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email.strip()))

def validate_date(date_str: str) -> bool:
    """Validate YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format."""
    if not date_str:
        return False
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            datetime.strptime(date_str.strip(), fmt)
            return True
        except ValueError:
            pass
    return False

def validate_positive_number(val: str, allow_zero: bool = False) -> bool:
    """Validate numeric input (float or int) > 0 (or >= 0 if allow_zero)."""
    try:
        num = float(val)
        if allow_zero:
            return num >= 0
        return num > 0
    except (ValueError, TypeError):
        return False

def format_currency(amount: float) -> str:
    """Format float into standard currency format e.g., $123.45."""
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def calculate_nights(check_in_str: str, check_out_str: str) -> int:
    """Calculate nights stay between dates, minimum 1 night."""
    fmt = "%Y-%m-%d"
    try:
        d1 = datetime.strptime(check_in_str.split()[0], fmt)
        d2 = datetime.strptime(check_out_str.split()[0], fmt)
        delta = (d2 - d1).days
        return max(1, delta)
    except Exception:
        return 1
