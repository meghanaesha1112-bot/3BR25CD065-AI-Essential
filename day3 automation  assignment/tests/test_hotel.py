import os
import tempfile
import pytest
from datetime import date, timedelta

from database import Database, hash_password
from utils import (
    validate_phone,
    validate_email,
    validate_date,
    validate_positive_number,
    format_currency,
    calculate_nights
)

@pytest.fixture
def test_db():
    """Fixture providing a temporary database instance for isolated testing."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    db = Database(db_path)
    yield db

    if os.path.exists(db_path):
        os.remove(db_path)

# --- Unit Tests: Utility Functions ---
def test_util_validations():
    # Phone validation
    assert validate_phone("+1-555-0199") is True
    assert validate_phone("1234567") is True
    assert validate_phone("123") is False
    assert validate_phone("") is False

    # Email validation
    assert validate_email("user@example.com") is True
    assert validate_email("") is True  # Optional empty email
    assert validate_email("invalid-email") is False

    # Date validation
    assert validate_date("2025-01-01") is True
    assert validate_date("2025-01-01 12:00:00") is True
    assert validate_date("invalid-date") is False

    # Positive number validation
    assert validate_positive_number("10.5") is True
    assert validate_positive_number("0", allow_zero=True) is True
    assert validate_positive_number("0", allow_zero=False) is False
    assert validate_positive_number("-5") is False
    assert validate_positive_number("abc") is False

    # Currency formatting
    assert format_currency(123.45) == "$123.45"
    assert format_currency(1000) == "$1,000.00"

    # Nights calculation
    assert calculate_nights("2025-05-01", "2025-05-05") == 4
    assert calculate_nights("2025-05-01", "2025-05-01") == 1  # minimum 1 night

# --- Integration Tests: Database Operations ---
def test_user_authentication(test_db):
    user = test_db.authenticate_user("admin", "admin123")
    assert user is not None
    assert user["username"] == "admin"
    assert user["role"] == "Admin"

    invalid_user = test_db.authenticate_user("admin", "wrongpass")
    assert invalid_user is None

def test_room_management(test_db):
    test_db.add_room("501", "Deluxe", 150.0, "Available")
    rooms = test_db.search_rooms("501")
    assert len(rooms) == 1
    assert rooms[0]["room_type"] == "Deluxe"

    test_db.update_room("501", "Suite", 220.0, "Available")
    rooms = test_db.search_rooms("501")
    assert rooms[0]["room_type"] == "Suite"
    assert rooms[0]["price_per_night"] == 220.0

    test_db.delete_room("501")
    rooms = test_db.search_rooms("501")
    assert len(rooms) == 0

def test_guest_management(test_db):
    guest_id = test_db.add_guest("Jane Smith", "+1-555-9999", "jane@example.com", "789 Pine St", "GOVT-999", 2)
    guest = test_db.get_guest_by_id(guest_id)
    assert guest is not None
    assert guest["full_name"] == "Jane Smith"

    test_db.update_guest(guest_id, "Jane Smith-Doe", "+1-555-9999", "jane@example.com", "789 Pine St", "GOVT-999", 3)
    guest = test_db.get_guest_by_id(guest_id)
    assert guest["full_name"] == "Jane Smith-Doe"
    assert guest["num_guests"] == 3

    test_db.delete_guest(guest_id)
    guest = test_db.get_guest_by_id(guest_id)
    assert guest is None

def test_double_booking_prevention(test_db):
    test_db.add_room("601", "Single", 60.0, "Available")
    guest_id = test_db.add_guest("Mark Test", "+1-555-8888", "mark@example.com", "Addr", "ID-1", 1)

    # First reservation
    check_in = "2025-06-01"
    check_out = "2025-06-05"
    res1_id = test_db.create_reservation(guest_id, "601", check_in, check_out, 1)
    assert res1_id > 0

    # Attempt overlapping reservation on same room
    overlap_check_in = "2025-06-03"
    overlap_check_out = "2025-06-07"
    with pytest.raises(ValueError, match="not available"):
        test_db.create_reservation(guest_id, "601", overlap_check_in, overlap_check_out, 1)

    # Non-overlapping reservation should succeed
    future_check_in = "2025-06-10"
    future_check_out = "2025-06-12"
    res2_id = test_db.create_reservation(guest_id, "601", future_check_in, future_check_out, 1)
    assert res2_id > 0

def test_checkin_checkout_billing_workflow(test_db):
    test_db.add_room("701", "Double", 100.0, "Available")
    guest_id = test_db.add_guest("Paul Walker", "+1-555-7777", "paul@example.com", "Addr", "ID-2", 2)

    # Perform Check-In
    check_in_time = "2025-05-10 12:00:00"
    exp_out = "2025-05-13"
    checkin_id = test_db.check_in_guest(guest_id, "701", check_in_time, exp_out)
    assert checkin_id > 0

    # Verify Room status updated to Occupied
    rooms = test_db.search_rooms("701")
    assert rooms[0]["status"] == "Occupied"

    # Add Service Charges
    test_db.add_service_charge(checkin_id, "Room Service", 2, 25.0)  # Total 50.0
    test_db.add_service_charge(checkin_id, "Laundry", 1, 15.0)       # Total 15.0
    total_services = test_db.get_total_services_amount(checkin_id)
    assert total_services == 65.0

    # Perform Check-Out & Settlement
    checkout_time = "2025-05-13 10:00:00"
    total_nights = 3
    room_charges = 3 * 100.0  # 300.0
    service_charges = 65.0
    tax_rate = 10.0
    tax_amount = (300.0 + 65.0) * 0.10  # 36.5
    discount = 15.0
    grand_total = (300.0 + 65.0) - 15.0 + 36.5  # 386.5

    checkout_id, bill_num = test_db.process_checkout(
        checkin_id=checkin_id,
        checkout_datetime=checkout_time,
        total_nights=total_nights,
        room_charges=room_charges,
        service_charges=service_charges,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        discount=discount,
        grand_total=grand_total
    )

    assert checkout_id > 0
    assert bill_num.startswith("BILL-")

    # Verify Room status returned to Available
    rooms = test_db.search_rooms("701")
    assert rooms[0]["status"] == "Available"

    # Verify bill recorded in database
    bills = test_db.search_bills(bill_num)
    assert len(bills) == 1
    assert bills[0]["grand_total"] == grand_total
