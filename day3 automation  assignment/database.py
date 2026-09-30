import os
import sqlite3
import hashlib
from datetime import datetime, date, timedelta

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "hotel.db")

def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class Database:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        # Ensure directory exists if using file path
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Create tables if they do not exist and seed initial sample data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'Staff',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 2. Rooms Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_number TEXT PRIMARY KEY,
                room_type TEXT NOT NULL,
                price_per_night REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Available'
            );
            """)

            # 3. Guests Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS guests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                address TEXT,
                govt_id TEXT NOT NULL,
                num_guests INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 4. Reservations Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_id INTEGER NOT NULL,
                room_number TEXT NOT NULL,
                check_in_date TEXT NOT NULL,
                check_out_date TEXT NOT NULL,
                num_guests INTEGER DEFAULT 1,
                status TEXT DEFAULT 'Reserved',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (guest_id) REFERENCES guests (id) ON DELETE CASCADE,
                FOREIGN KEY (room_number) REFERENCES rooms (room_number) ON DELETE CASCADE
            );
            """)

            # 5. Checkins Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reservation_id INTEGER,
                guest_id INTEGER NOT NULL,
                room_number TEXT NOT NULL,
                check_in_date TEXT NOT NULL,
                expected_check_out TEXT NOT NULL,
                status TEXT DEFAULT 'Active',
                FOREIGN KEY (reservation_id) REFERENCES reservations (id) ON DELETE SET NULL,
                FOREIGN KEY (guest_id) REFERENCES guests (id),
                FOREIGN KEY (room_number) REFERENCES rooms (room_number)
            );
            """)

            # 6. Checkouts Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checkin_id INTEGER NOT NULL,
                guest_id INTEGER NOT NULL,
                room_number TEXT NOT NULL,
                check_in_date TEXT NOT NULL,
                check_out_date TEXT NOT NULL,
                total_nights INTEGER NOT NULL,
                room_charges REAL NOT NULL,
                service_charges REAL DEFAULT 0.0,
                tax_amount REAL DEFAULT 0.0,
                discount_amount REAL DEFAULT 0.0,
                grand_total REAL NOT NULL,
                FOREIGN KEY (checkin_id) REFERENCES checkins (id),
                FOREIGN KEY (guest_id) REFERENCES guests (id),
                FOREIGN KEY (room_number) REFERENCES rooms (room_number)
            );
            """)

            # 7. Services Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checkin_id INTEGER NOT NULL,
                service_name TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                price REAL NOT NULL,
                total_amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (checkin_id) REFERENCES checkins (id) ON DELETE CASCADE
            );
            """)

            # 8. Bills Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_number TEXT UNIQUE NOT NULL,
                checkout_id INTEGER NOT NULL,
                guest_id INTEGER NOT NULL,
                room_number TEXT NOT NULL,
                check_in_date TEXT NOT NULL,
                check_out_date TEXT NOT NULL,
                total_nights INTEGER NOT NULL,
                room_price_per_night REAL NOT NULL,
                room_charges REAL NOT NULL,
                service_charges REAL NOT NULL,
                tax_rate REAL DEFAULT 10.0,
                tax_amount REAL NOT NULL,
                discount REAL DEFAULT 0.0,
                grand_total REAL NOT NULL,
                payment_status TEXT DEFAULT 'Paid',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (checkout_id) REFERENCES checkouts (id),
                FOREIGN KEY (guest_id) REFERENCES guests (id)
            );
            """)

            conn.commit()

            # Seed default users and sample data if empty
            self._seed_sample_data(conn)

    def _seed_sample_data(self, conn):
        cursor = conn.cursor()

        # Check default user
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                ("admin", hash_password("admin123"), "System Administrator", "Admin")
            )
            cursor.execute(
                "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                ("staff", hash_password("staff123"), "Hotel Staff", "Staff")
            )

        # Check default rooms
        cursor.execute("SELECT COUNT(*) FROM rooms")
        if cursor.fetchone()[0] == 0:
            sample_rooms = [
                ("101", "Single", 50.0, "Available"),
                ("102", "Single", 55.0, "Available"),
                ("201", "Double", 80.0, "Available"),
                ("202", "Double", 85.0, "Reserved"),
                ("301", "Deluxe", 120.0, "Occupied"),
                ("302", "Deluxe", 130.0, "Available"),
                ("401", "Suite", 200.0, "Available"),
                ("402", "Suite", 250.0, "Maintenance")
            ]
            cursor.executemany(
                "INSERT INTO rooms (room_number, room_type, price_per_night, status) VALUES (?, ?, ?, ?)",
                sample_rooms
            )

        # Check default guests
        cursor.execute("SELECT COUNT(*) FROM guests")
        if cursor.fetchone()[0] == 0:
            sample_guests = [
                ("John Doe", "+1-555-0192", "john.doe@example.com", "123 Main St, Springfield", "GOVT-ID-101", 2),
                ("Alice Smith", "+1-555-0184", "alice.smith@example.com", "456 Oak Ave, Metropolis", "GOVT-ID-102", 1),
                ("Robert Johnson", "+1-555-0133", "robert.j@example.com", "789 Pine Rd, Gotham", "GOVT-ID-103", 3)
            ]
            cursor.executemany(
                "INSERT INTO guests (full_name, phone, email, address, govt_id, num_guests) VALUES (?, ?, ?, ?, ?, ?)",
                sample_guests
            )

        # Check default reservations & checkins
        cursor.execute("SELECT COUNT(*) FROM reservations")
        if cursor.fetchone()[0] == 0:
            today_str = date.today().strftime("%Y-%m-%d")
            tomorrow_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
            next_week_str = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")

            cursor.execute(
                "INSERT INTO reservations (guest_id, room_number, check_in_date, check_out_date, num_guests, status) VALUES (?, ?, ?, ?, ?, ?)",
                (2, "202", today_str, tomorrow_str, 1, "Reserved")
            )
            res_id = cursor.lastrowid

            # Active checkin for guest 1 room 301
            cursor.execute(
                "INSERT INTO checkins (reservation_id, guest_id, room_number, check_in_date, expected_check_out, status) VALUES (?, ?, ?, ?, ?, ?)",
                (None, 1, "301", f"{today_str} 10:00:00", next_week_str, "Active")
            )

        conn.commit()

    # User Authentication
    def authenticate_user(self, username, password):
        hashed = hash_password(password)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, full_name, role FROM users WHERE username = ? AND password = ?",
                (username, hashed)
            )
            return cursor.fetchone()

    # Room Operations
    def get_all_rooms(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms ORDER BY room_number ASC")
            return cursor.fetchall()

    def add_room(self, room_number, room_type, price, status="Available"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO rooms (room_number, room_type, price_per_night, status) VALUES (?, ?, ?, ?)",
                (room_number, room_type, float(price), status)
            )
            conn.commit()

    def update_room(self, room_number, room_type, price, status):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE rooms SET room_type = ?, price_per_night = ?, status = ? WHERE room_number = ?",
                (room_type, float(price), status, room_number)
            )
            conn.commit()

    def delete_room(self, room_number):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rooms WHERE room_number = ?", (room_number,))
            conn.commit()

    def update_room_status(self, room_number, status):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE rooms SET status = ? WHERE room_number = ?", (status, room_number))
            conn.commit()

    def search_rooms(self, search_term):
        term = f"%{search_term}%"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM rooms WHERE room_number LIKE ? OR room_type LIKE ? OR status LIKE ?",
                (term, term, term)
            )
            return cursor.fetchall()

    # Guest Operations
    def get_all_guests(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM guests ORDER BY id DESC")
            return cursor.fetchall()

    def add_guest(self, full_name, phone, email, address, govt_id, num_guests=1):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO guests (full_name, phone, email, address, govt_id, num_guests) VALUES (?, ?, ?, ?, ?, ?)",
                (full_name, phone, email, address, govt_id, int(num_guests))
            )
            conn.commit()
            return cursor.lastrowid

    def update_guest(self, guest_id, full_name, phone, email, address, govt_id, num_guests):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE guests SET full_name = ?, phone = ?, email = ?, address = ?, govt_id = ?, num_guests = ? WHERE id = ?",
                (full_name, phone, email, address, govt_id, int(num_guests), int(guest_id))
            )
            conn.commit()

    def delete_guest(self, guest_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM guests WHERE id = ?", (int(guest_id),))
            conn.commit()

    def search_guests(self, search_term):
        term = f"%{search_term}%"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM guests WHERE full_name LIKE ? OR phone LIKE ? OR email LIKE ? OR govt_id LIKE ?",
                (term, term, term, term)
            )
            return cursor.fetchall()

    def get_guest_by_id(self, guest_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM guests WHERE id = ?", (int(guest_id),))
            return cursor.fetchone()

    # Reservation Operations
    def is_room_available_for_dates(self, room_number, check_in_date, check_out_date, exclude_res_id=None):
        """Check if room has conflicting active reservations or active checkins."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # First check if room is under maintenance
            cursor.execute("SELECT status FROM rooms WHERE room_number = ?", (room_number,))
            room = cursor.fetchone()
            if not room or room["status"] == "Maintenance":
                return False

            # Check active reservations
            query = """
            SELECT COUNT(*) FROM reservations
            WHERE room_number = ? AND status IN ('Reserved', 'Checked-In')
            AND (check_in_date < ? AND check_out_date > ?)
            """
            params = [room_number, check_out_date, check_in_date]
            if exclude_res_id:
                query += " AND id != ?"
                params.append(exclude_res_id)

            cursor.execute(query, params)
            count = cursor.fetchone()[0]

            if count > 0:
                return False

            # Check active checkins
            cursor.execute(
                "SELECT COUNT(*) FROM checkins WHERE room_number = ? AND status = 'Active'",
                (room_number,)
            )
            active_checkins = cursor.fetchone()[0]
            if active_checkins > 0:
                return False

            return True

    def create_reservation(self, guest_id, room_number, check_in_date, check_out_date, num_guests=1):
        if not self.is_room_available_for_dates(room_number, check_in_date, check_out_date):
            raise ValueError(f"Room {room_number} is not available for selected dates ({check_in_date} to {check_out_date}).")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reservations (guest_id, room_number, check_in_date, check_out_date, num_guests, status) VALUES (?, ?, ?, ?, ?, 'Reserved')",
                (int(guest_id), room_number, check_in_date, check_out_date, int(num_guests))
            )
            # Update room status to Reserved if starting today or near term
            cursor.execute("UPDATE rooms SET status = 'Reserved' WHERE room_number = ? AND status = 'Available'", (room_number,))
            conn.commit()
            return cursor.lastrowid

    def update_reservation(self, res_id, guest_id, room_number, check_in_date, check_out_date, num_guests, status):
        if status in ['Reserved', 'Checked-In'] and not self.is_room_available_for_dates(room_number, check_in_date, check_out_date, exclude_res_id=res_id):
            raise ValueError(f"Room {room_number} is not available for selected dates.")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE reservations SET guest_id = ?, room_number = ?, check_in_date = ?, check_out_date = ?, num_guests = ?, status = ? WHERE id = ?",
                (int(guest_id), room_number, check_in_date, check_out_date, int(num_guests), status, int(res_id))
            )
            conn.commit()

    def cancel_reservation(self, res_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT room_number FROM reservations WHERE id = ?", (int(res_id),))
            res = cursor.fetchone()
            if res:
                room_num = res["room_number"]
                cursor.execute("UPDATE reservations SET status = 'Cancelled' WHERE id = ?", (int(res_id),))
                # Restore room status if no other active reservation/checkin
                cursor.execute("SELECT COUNT(*) FROM reservations WHERE room_number = ? AND status = 'Reserved'", (room_num,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("SELECT COUNT(*) FROM checkins WHERE room_number = ? AND status = 'Active'", (room_num,))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("UPDATE rooms SET status = 'Available' WHERE room_number = ?", (room_num,))
            conn.commit()

    def get_all_reservations(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT r.*, g.full_name as guest_name, g.phone as guest_phone
            FROM reservations r
            JOIN guests g ON r.guest_id = g.id
            ORDER BY r.id DESC
            """)
            return cursor.fetchall()

    def search_reservations(self, search_term):
        term = f"%{search_term}%"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT r.*, g.full_name as guest_name, g.phone as guest_phone
            FROM reservations r
            JOIN guests g ON r.guest_id = g.id
            WHERE g.full_name LIKE ? OR r.room_number LIKE ? OR r.status LIKE ? OR CAST(r.id AS TEXT) LIKE ?
            ORDER BY r.id DESC
            """, (term, term, term, term))
            return cursor.fetchall()

    # Check-in Operations
    def check_in_guest(self, guest_id, room_number, check_in_datetime, expected_check_out, reservation_id=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Verify room is available or reserved for this guest/reservation
            cursor.execute("SELECT status FROM rooms WHERE room_number = ?", (room_number,))
            room = cursor.fetchone()
            if not room:
                raise ValueError("Room does not exist.")
            if room["status"] == "Occupied":
                raise ValueError(f"Room {room_number} is currently occupied.")
            if room["status"] == "Maintenance":
                raise ValueError(f"Room {room_number} is under maintenance.")

            cursor.execute(
                "INSERT INTO checkins (reservation_id, guest_id, room_number, check_in_date, expected_check_out, status) VALUES (?, ?, ?, ?, ?, 'Active')",
                (reservation_id, int(guest_id), room_number, check_in_datetime, expected_check_out)
            )
            checkin_id = cursor.lastrowid

            if reservation_id:
                cursor.execute("UPDATE reservations SET status = 'Checked-In' WHERE id = ?", (int(reservation_id),))

            cursor.execute("UPDATE rooms SET status = 'Occupied' WHERE room_number = ?", (room_number,))
            conn.commit()
            return checkin_id

    def get_active_checkins(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT c.*, g.full_name as guest_name, g.phone as guest_phone, rm.price_per_night, rm.room_type
            FROM checkins c
            JOIN guests g ON c.guest_id = g.id
            JOIN rooms rm ON c.room_number = rm.room_number
            WHERE c.status = 'Active'
            ORDER BY c.id DESC
            """)
            return cursor.fetchall()

    # Services Operations
    def add_service_charge(self, checkin_id, service_name, quantity, price):
        qty = int(quantity)
        p = float(price)
        total = qty * p
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO services (checkin_id, service_name, quantity, price, total_amount) VALUES (?, ?, ?, ?, ?)",
                (int(checkin_id), service_name, qty, p, total)
            )
            conn.commit()
            return cursor.lastrowid

    def get_services_for_checkin(self, checkin_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM services WHERE checkin_id = ? ORDER BY id ASC", (int(checkin_id),))
            return cursor.fetchall()

    def get_total_services_amount(self, checkin_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(total_amount) FROM services WHERE checkin_id = ?", (int(checkin_id),))
            val = cursor.fetchone()[0]
            return val if val else 0.0

    def delete_service_charge(self, service_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM services WHERE id = ?", (int(service_id),))
            conn.commit()

    # Check-out & Billing Operations
    def process_checkout(self, checkin_id, checkout_datetime, total_nights, room_charges, service_charges, tax_rate, tax_amount, discount, grand_total):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM checkins WHERE id = ?", (int(checkin_id),))
            checkin = cursor.fetchone()
            if not checkin or checkin["status"] != "Active":
                raise ValueError("Invalid or non-active checkin record.")

            # Record Checkout
            cursor.execute("""
            INSERT INTO checkouts (checkin_id, guest_id, room_number, check_in_date, check_out_date, total_nights, room_charges, service_charges, tax_amount, discount_amount, grand_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (int(checkin_id), checkin["guest_id"], checkin["room_number"], checkin["check_in_date"], checkout_datetime, int(total_nights), float(room_charges), float(service_charges), float(tax_amount), float(discount), float(grand_total)))

            checkout_id = cursor.lastrowid

            # Update checkin status
            cursor.execute("UPDATE checkins SET status = 'Checked-Out' WHERE id = ?", (int(checkin_id),))

            # Update room status to Available
            cursor.execute("UPDATE rooms SET status = 'Available' WHERE room_number = ?", (checkin["room_number"],))

            # Generate Bill Record
            bill_num = f"BILL-{checkout_id:05d}-{datetime.now().strftime('%Y%m%d')}"
            cursor.execute("SELECT price_per_night FROM rooms WHERE room_number = ?", (checkin["room_number"],))
            r_price = cursor.fetchone()["price_per_night"]

            cursor.execute("""
            INSERT INTO bills (bill_number, checkout_id, guest_id, room_number, check_in_date, check_out_date, total_nights, room_price_per_night, room_charges, service_charges, tax_rate, tax_amount, discount, grand_total, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Paid')
            """, (bill_num, checkout_id, checkin["guest_id"], checkin["room_number"], checkin["check_in_date"], checkout_datetime, int(total_nights), float(r_price), float(room_charges), float(service_charges), float(tax_rate), float(tax_amount), float(discount), float(grand_total)))

            conn.commit()
            return checkout_id, bill_num

    def get_all_bills(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT b.*, g.full_name as guest_name
            FROM bills b
            JOIN guests g ON b.guest_id = g.id
            ORDER BY b.id DESC
            """)
            return cursor.fetchall()

    def search_bills(self, search_term):
        term = f"%{search_term}%"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT b.*, g.full_name as guest_name
            FROM bills b
            JOIN guests g ON b.guest_id = g.id
            WHERE b.bill_number LIKE ? OR g.full_name LIKE ? OR b.room_number LIKE ?
            ORDER BY b.id DESC
            """, (term, term, term))
            return cursor.fetchall()

    def get_dashboard_metrics(self):
        today_str = date.today().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM rooms")
            total_rooms = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Available'")
            available_rooms = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Occupied'")
            occupied_rooms = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Reserved'")
            reserved_rooms = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM guests")
            total_guests = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM checkins WHERE date(check_in_date) = date(?)", (today_str,))
            today_checkins = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM checkouts WHERE date(check_out_date) = date(?)", (today_str,))
            today_checkouts = cursor.fetchone()[0]

            return {
                "total_rooms": total_rooms,
                "available_rooms": available_rooms,
                "occupied_rooms": occupied_rooms,
                "reserved_rooms": reserved_rooms,
                "total_guests": total_guests,
                "today_checkins": today_checkins,
                "today_checkouts": today_checkouts
            }
