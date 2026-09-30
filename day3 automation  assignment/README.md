# Hotel Management System 🏨

A complete, professional desktop application built with **Python 3**, **Tkinter**, and **SQLite**. Designed for hotel administrative staff to efficiently manage rooms, guest records, reservations, check-ins, check-outs, itemized billing, and financial reports.

---

## 📌 Project Overview

### Problem Statement
Managing hotel operations manually or with disconnected spreadsheets leads to double-booked rooms, billing errors, guest tracking difficulties, and delayed administrative reporting.

### Objectives
* Automate core front-desk operations (check-in, check-out, billing, room assignment).
* Prevent room double-booking using SQLite integrity constraints and date overlap queries.
* Maintain complete records of guest histories, room statuses, service charges, and receipts.
* Provide an intuitive, beginner-friendly desktop interface with clear feedback and validations.

---

## ✨ Features

### 1. User Authentication System
* SQLite-backed authentication with SHA-256 hashed passwords.
* Clean login screen with input reset and application exit options.
* Pre-configured demonstration accounts for Admin and Staff roles.

### 2. Live Interactive Dashboard
* Real-time metrics overview:
  * Total Rooms
  * Available Rooms
  * Occupied Rooms
  * Reserved Rooms
  * Total Registered Guests
  * Today's Check-ins
  * Today's Check-outs
* One-click navigation sidebar and quick action grid.

### 3. Room Management
* Room Types: `Single`, `Double`, `Deluxe`, `Suite`.
* Status Tracking: `Available`, `Reserved`, `Occupied`, `Maintenance`.
* Search and filter rooms by room number or type.
* Full CRUD capabilities with primary key protection during editing.

### 4. Guest Management
* Complete guest profile tracking (Full Name, Phone, Email, Address, Government ID, Guests count).
* Instant search across guest records by name, phone, email, or ID.
* Strict input validation (e.g., valid phone numbers, email structure).

### 5. Reservation Management & Double-Booking Prevention
* Create, search, update, and cancel reservations.
* **Double-Booking Prevention**: Checks for date-range overlaps against active reservations and current room occupants before confirming booking.

### 6. Fast Check-In System
* Assign available rooms or link existing active reservations.
* Real-time timestamp logging for arrival and expected departure.
* Automatic status update of selected room to `Occupied`.

### 7. Check-Out & Automated Settlement
* Select active occupants and automatically calculate duration of stay in nights.
* Compute room charges based on room rate and stay duration.
* Pull all linked extra service charges into total calculation.
* Flexible tax (%) and discount ($) adjustments.
* Resets room status back to `Available` upon completion.

### 8. Services & Extra Charges
* Charge extra hotel amenities directly to guest room accounts:
  * Food & Beverage
  * Laundry Service
  * Room Service / In-Room Dining
  * Airport Transport
  * Spa & Wellness
* Itemized charge ledger with add and remove capabilities.

### 9. Billing & Receipt Generation
* Generates unique itemized invoices (e.g., `BILL-00001-20250520`).
* Printable receipt view formatted with business headers and breakdown.
* Export receipts to plain text (`.txt`) files.

### 10. Comprehensive Reports & Audits
* Tabbed reporting interface:
  * Rooms Status Matrix
  * Guest Registry
  * Reservations Log
  * Active Occupants List
  * Total Revenue & Payment History

---

## 🛠️ Technology Stack

* **Language**: Python 3.12+
* **GUI Toolkit**: Tkinter (Standard Library)
* **Database**: SQLite3 (Embedded SQL with Foreign Keys enabled)
* **Testing Framework**: `pytest`
* **Virtual X11 / Headless Testing**: `xvfb-run`

---

## 📁 Directory Structure

```text
hotel_management/
│
├── main.py              # Main application window & navigation controller
├── database.py          # SQLite schema, connection pool & CRUD operations
├── login.py             # User authentication screen
├── dashboard.py         # Summary metrics & quick navigation dashboard
├── rooms.py             # Room management frame
├── guests.py            # Guest management frame
├── reservations.py     # Reservation management frame & clash checks
├── checkin.py           # Front desk check-in module
├── checkout.py          # Check-out & billing calculation module
├── services.py          # Additional room service charges module
├── billing.py           # Invoicing history & receipt export module
├── reports.py           # Multi-tab administrative reports frame
├── utils.py             # Validation helpers & currency/date formatting
├── database/
│   └── hotel.db         # SQLite database file (created automatically)
├── tests/
│   └── test_hotel.py    # Automated test suite (pytest)
├── README.md            # Comprehensive documentation
└── requirements.txt     # Python dependencies
```

---

## 🗄️ Database Design

The system automatically initializes `database/hotel.db` on launch with the following schema:

* `users` (`id`, `username`, `password`, `full_name`, `role`, `created_at`)
* `rooms` (`room_number` PK, `room_type`, `price_per_night`, `status`)
* `guests` (`id` PK, `full_name`, `phone`, `email`, `address`, `govt_id`, `num_guests`, `created_at`)
* `reservations` (`id` PK, `guest_id` FK, `room_number` FK, `check_in_date`, `check_out_date`, `num_guests`, `status`)
* `checkins` (`id` PK, `reservation_id` FK, `guest_id` FK, `room_number` FK, `check_in_date`, `expected_check_out`, `status`)
* `checkouts` (`id` PK, `checkin_id` FK, `guest_id` FK, `room_number` FK, `check_in_date`, `check_out_date`, `total_nights`, `room_charges`, `service_charges`, `tax_amount`, `discount_amount`, `grand_total`)
* `services` (`id` PK, `checkin_id` FK, `service_name`, `quantity`, `price`, `total_amount`, `created_at`)
* `bills` (`id` PK, `bill_number` UNIQUE, `checkout_id` FK, `guest_id` FK, `room_number`, `check_in_date`, `check_out_date`, `total_nights`, `room_price_per_night`, `room_charges`, `service_charges`, `tax_rate`, `tax_amount`, `discount`, `grand_total`, `payment_status`, `created_at`)

---

## 🔑 Default Login Credentials

The database comes pre-seeded with sample rooms, guests, and default user accounts:

| Role | Username | Password |
| :--- | :--- | :--- |
| **System Administrator** | `admin` | `admin123` |
| **Hotel Staff** | `staff` | `staff123` |

---

## 🚀 Installation & How to Run

### Prerequisites
* Python 3.8 or higher installed on your operating system.
* Tkinter package (included by default in standard Python installers on Windows/Mac, or via `sudo apt install python3-tk` on Linux).

### Running the Application
1. Clone or extract the project directory.
2. Navigate to the project root directory:
   ```bash
   cd hotel_management
   ```
3. Run the application:
   ```bash
   python3 main.py
   ```

### Running Automated Tests
To run the full test suite with `pytest`:
```bash
PYTHONPATH=. pytest tests/
```

---

## 🔮 Future Enhancements
* Multi-language / Localization support for international guests.
* Email dispatch of PDF invoices directly to guests.
* Barcode / QR code scanning for guest check-in identification.
* Dark mode graphical user interface option.

---

## 📝 Conclusion
This Hotel Management System provides a complete software solution for hotel operations. Built using modular Object-Oriented principles and standard Python libraries, it is reliable, maintainable, and ideal for educational demonstrations or practical deployments.
