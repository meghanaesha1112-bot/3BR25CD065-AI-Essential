import tkinter as tk
from tkinter import ttk, messagebox
from utils import format_currency

class ReportsFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        self._build_ui()
        self.load_report_data()

    def _build_ui(self):
        # Header / Title Frame
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Reports & System Audits", font=("Helvetica", 16, "bold"), foreground="#2C3E50").pack(side="left")

        btn_refresh = ttk.Button(header, text="Reset / Refresh", command=self.load_report_data)
        btn_refresh.pack(side="right")

        # Tabs notebook for different reports
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: All Rooms Status
        self.tab_rooms = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_rooms, text=" 🏨 Rooms Status ")
        self._build_rooms_tab()

        # Tab 2: Guest Registry
        self.tab_guests = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_guests, text=" 👥 Guest Registry ")
        self._build_guests_tab()

        # Tab 3: Reservations Audit
        self.tab_reservations = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_reservations, text=" 📅 Reservations ")
        self._build_reservations_tab()

        # Tab 4: Current Occupants
        self.tab_occupants = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_occupants, text=" 🔑 Active Occupants ")
        self._build_occupants_tab()

        # Tab 5: Billing & Revenue History
        self.tab_revenue = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_revenue, text=" 💳 Revenue & Billing ")
        self._build_revenue_tab()

    def _build_rooms_tab(self):
        cols = ("room_number", "room_type", "price_per_night", "status")
        tree = ttk.Treeview(self.tab_rooms, columns=cols, show="headings")
        tree.heading("room_number", text="Room No.")
        tree.heading("room_type", text="Type")
        tree.heading("price_per_night", text="Price / Night")
        tree.heading("status", text="Current Status")

        tree.column("room_number", anchor="center")
        tree.column("room_type", anchor="center")
        tree.column("price_per_night", anchor="e")
        tree.column("status", anchor="center")

        sb = ttk.Scrollbar(self.tab_rooms, orient="vertical", command=tree.yview)
        tree.configure(yscroll=sb.set)

        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_rooms = tree

    def _build_guests_tab(self):
        cols = ("id", "full_name", "phone", "email", "govt_id", "num_guests")
        tree = ttk.Treeview(self.tab_guests, columns=cols, show="headings")
        tree.heading("id", text="Guest ID")
        tree.heading("full_name", text="Full Name")
        tree.heading("phone", text="Phone")
        tree.heading("email", text="Email")
        tree.heading("govt_id", text="Govt ID")
        tree.heading("num_guests", text="Guests")

        tree.column("id", width=60, anchor="center")
        tree.column("full_name", anchor="w")
        tree.column("phone", anchor="center")
        tree.column("email", anchor="w")
        tree.column("govt_id", anchor="center")
        tree.column("num_guests", width=60, anchor="center")

        sb = ttk.Scrollbar(self.tab_guests, orient="vertical", command=tree.yview)
        tree.configure(yscroll=sb.set)

        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_guests = tree

    def _build_reservations_tab(self):
        cols = ("id", "guest_name", "room_number", "check_in_date", "check_out_date", "status")
        tree = ttk.Treeview(self.tab_reservations, columns=cols, show="headings")
        tree.heading("id", text="Res ID")
        tree.heading("guest_name", text="Guest Name")
        tree.heading("room_number", text="Room No.")
        tree.heading("check_in_date", text="Check-In Date")
        tree.heading("check_out_date", text="Check-Out Date")
        tree.heading("status", text="Status")

        tree.column("id", width=60, anchor="center")
        tree.column("guest_name", anchor="w")
        tree.column("room_number", width=80, anchor="center")
        tree.column("check_in_date", anchor="center")
        tree.column("check_out_date", anchor="center")
        tree.column("status", anchor="center")

        sb = ttk.Scrollbar(self.tab_reservations, orient="vertical", command=tree.yview)
        tree.configure(yscroll=sb.set)

        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_res = tree

    def _build_occupants_tab(self):
        cols = ("id", "guest_name", "room_number", "check_in_date", "expected_check_out")
        tree = ttk.Treeview(self.tab_occupants, columns=cols, show="headings")
        tree.heading("id", text="Check-In ID")
        tree.heading("guest_name", text="Guest Name")
        tree.heading("room_number", text="Room No.")
        tree.heading("check_in_date", text="Check-In Time")
        tree.heading("expected_check_out", text="Expected Check-Out")

        tree.column("id", width=80, anchor="center")
        tree.column("guest_name", anchor="w")
        tree.column("room_number", width=80, anchor="center")
        tree.column("check_in_date", anchor="center")
        tree.column("expected_check_out", anchor="center")

        sb = ttk.Scrollbar(self.tab_occupants, orient="vertical", command=tree.yview)
        tree.configure(yscroll=sb.set)

        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_occupants = tree

    def _build_revenue_tab(self):
        frame = ttk.Frame(self.tab_revenue)
        frame.pack(fill="both", expand=True)

        cols = ("bill_number", "guest_name", "room_number", "total_nights", "grand_total", "created_at")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        tree.heading("bill_number", text="Bill No.")
        tree.heading("guest_name", text="Guest Name")
        tree.heading("room_number", text="Room No.")
        tree.heading("total_nights", text="Nights")
        tree.heading("grand_total", text="Total Paid")
        tree.heading("created_at", text="Issued Date")

        tree.column("bill_number", anchor="center")
        tree.column("guest_name", anchor="w")
        tree.column("room_number", width=80, anchor="center")
        tree.column("total_nights", width=60, anchor="center")
        tree.column("grand_total", anchor="e")
        tree.column("created_at", anchor="center")

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=sb.set)

        tree.pack(side="top", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Bottom Revenue Summary Bar
        summary_bar = ttk.Frame(frame, padding="10 10 10 0")
        summary_bar.pack(side="bottom", fill="x")

        ttk.Label(summary_bar, text="Total Revenue Collected:", font=("Helvetica", 11, "bold")).pack(side="left")
        self.lbl_total_revenue = ttk.Label(summary_bar, text="$0.00", font=("Helvetica", 13, "bold"), foreground="#27AE60")
        self.lbl_total_revenue.pack(side="left", padx=10)

        self.tree_revenue = tree

    def load_report_data(self):
        # 1. Rooms
        for item in self.tree_rooms.get_children():
            self.tree_rooms.delete(item)
        for r in self.db.get_all_rooms():
            self.tree_rooms.insert("", "end", values=(r["room_number"], r["room_type"], format_currency(r["price_per_night"]), r["status"]))

        # 2. Guests
        for item in self.tree_guests.get_children():
            self.tree_guests.delete(item)
        for g in self.db.get_all_guests():
            self.tree_guests.insert("", "end", values=(g["id"], g["full_name"], g["phone"], g["email"] or "", g["govt_id"], g["num_guests"]))

        # 3. Reservations
        for item in self.tree_res.get_children():
            self.tree_res.delete(item)
        for res in self.db.get_all_reservations():
            self.tree_res.insert("", "end", values=(res["id"], res["guest_name"], res["room_number"], res["check_in_date"], res["check_out_date"], res["status"]))

        # 4. Occupants
        for item in self.tree_occupants.get_children():
            self.tree_occupants.delete(item)
        for occ in self.db.get_active_checkins():
            self.tree_occupants.insert("", "end", values=(occ["id"], occ["guest_name"], occ["room_number"], occ["check_in_date"], occ["expected_check_out"]))

        # 5. Revenue / Bills
        for item in self.tree_revenue.get_children():
            self.tree_revenue.delete(item)
        bills = self.db.get_all_bills()
        total_rev = 0.0
        for b in bills:
            total_rev += b["grand_total"]
            self.tree_revenue.insert("", "end", values=(b["bill_number"], b["guest_name"], b["room_number"], b["total_nights"], format_currency(b["grand_total"]), b["created_at"]))

        self.lbl_total_revenue.config(text=format_currency(total_rev))
