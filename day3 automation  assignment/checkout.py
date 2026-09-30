import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from utils import calculate_nights, format_currency, validate_positive_number

class CheckOutFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        self._build_ui()
        self.load_active_checkins()

    def _build_ui(self):
        # Header / Title Frame
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Guest Check-Out & Billing Calculation", font=("Helvetica", 16, "bold"), foreground="#2C3E50").pack(side="left")

        btn_refresh = ttk.Button(header, text="Reset / Refresh", command=self.load_active_checkins)
        btn_refresh.pack(side="right")

        main_paned = ttk.PanedWindow(self, orient="horizontal")
        main_paned.pack(fill="both", expand=True)

        # --- Left Table (Active Occupants) ---
        table_frame = ttk.LabelFrame(main_paned, text=" Select Active Occupant for Check-Out ", padding="10 10 10 10")
        main_paned.add(table_frame, weight=3)

        columns = ("id", "guest_name", "room_number", "room_type", "price", "check_in_date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="Check-In ID")
        self.tree.heading("guest_name", text="Guest Name")
        self.tree.heading("room_number", text="Room No.")
        self.tree.heading("room_type", text="Room Type")
        self.tree.heading("price", text="Price / Night")
        self.tree.heading("check_in_date", text="Check-In Date")

        self.tree.column("id", width=70, anchor="center")
        self.tree.column("guest_name", width=130, anchor="w")
        self.tree.column("room_number", width=70, anchor="center")
        self.tree.column("room_type", width=90, anchor="center")
        self.tree.column("price", width=90, anchor="e")
        self.tree.column("check_in_date", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # --- Right Summary & Settlement Form Frame ---
        form_frame = ttk.LabelFrame(main_paned, text=" Checkout Billing Statement ", padding="15 15 15 15")
        main_paned.add(form_frame, weight=2)

        # Selected Info Summary
        ttk.Label(form_frame, text="Check-In ID:").grid(row=0, column=0, sticky="w", pady=4)
        self.lbl_id = ttk.Label(form_frame, text="-", font=("Helvetica", 10, "bold"))
        self.lbl_id.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(form_frame, text="Guest Name:").grid(row=1, column=0, sticky="w", pady=4)
        self.lbl_guest = ttk.Label(form_frame, text="-", font=("Helvetica", 10, "bold"))
        self.lbl_guest.grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(form_frame, text="Room Number:").grid(row=2, column=0, sticky="w", pady=4)
        self.lbl_room = ttk.Label(form_frame, text="-", font=("Helvetica", 10, "bold"))
        self.lbl_room.grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(form_frame, text="Check-In Date:").grid(row=3, column=0, sticky="w", pady=4)
        self.lbl_checkin_date = ttk.Label(form_frame, text="-")
        self.lbl_checkin_date.grid(row=3, column=1, sticky="w", pady=4)

        ttk.Label(form_frame, text="Check-Out Date:").grid(row=4, column=0, sticky="w", pady=4)
        self.ent_checkout_date = ttk.Entry(form_frame, width=20)
        self.ent_checkout_date.grid(row=4, column=1, sticky="w", pady=4)

        ttk.Label(form_frame, text="Total Stay Nights:").grid(row=5, column=0, sticky="w", pady=4)
        self.lbl_nights = ttk.Label(form_frame, text="0", font=("Helvetica", 10, "bold"))
        self.lbl_nights.grid(row=5, column=1, sticky="w", pady=4)

        ttk.Separator(form_frame, orient="horizontal").grid(row=6, column=0, columnspan=2, sticky="ew", pady=8)

        # Charges Breakdown
        ttk.Label(form_frame, text="Room Charges:").grid(row=7, column=0, sticky="w", pady=4)
        self.lbl_room_charges = ttk.Label(form_frame, text="$0.00")
        self.lbl_room_charges.grid(row=7, column=1, sticky="w", pady=4)

        ttk.Label(form_frame, text="Service Charges:").grid(row=8, column=0, sticky="w", pady=4)
        self.lbl_service_charges = ttk.Label(form_frame, text="$0.00")
        self.lbl_service_charges.grid(row=8, column=1, sticky="w", pady=4)

        ttk.Label(form_frame, text="Tax Rate (%):").grid(row=9, column=0, sticky="w", pady=4)
        self.ent_tax_rate = ttk.Entry(form_frame, width=10)
        self.ent_tax_rate.insert(0, "10.0")
        self.ent_tax_rate.grid(row=9, column=1, sticky="w", pady=4)

        ttk.Label(form_frame, text="Discount ($):").grid(row=10, column=0, sticky="w", pady=4)
        self.ent_discount = ttk.Entry(form_frame, width=10)
        self.ent_discount.insert(0, "0.00")
        self.ent_discount.grid(row=10, column=1, sticky="w", pady=4)

        ttk.Separator(form_frame, orient="horizontal").grid(row=11, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Label(form_frame, text="Grand Total:", font=("Helvetica", 12, "bold"), foreground="#27AE60").grid(row=12, column=0, sticky="w", pady=6)
        self.lbl_grand_total = ttk.Label(form_frame, text="$0.00", font=("Helvetica", 14, "bold"), foreground="#27AE60")
        self.lbl_grand_total.grid(row=12, column=1, sticky="w", pady=6)

        # Action Buttons
        btn_box = ttk.Frame(form_frame)
        btn_box.grid(row=13, column=0, columnspan=2, pady=(15, 0), sticky="ew")

        btn_calc = ttk.Button(btn_box, text="Calculate Bill", command=self.calculate_bill)
        btn_calc.pack(side="left", expand=True, fill="x", padx=2)

        btn_checkout = ttk.Button(btn_box, text="Complete Check-Out 🚪", command=self.perform_checkout)
        btn_checkout.pack(side="left", expand=True, fill="x", padx=2)

        # Store calculated details internally
        self.current_checkin = None
        self.calc_data = {}

    def load_active_checkins(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.clear_form()
        checkins = self.db.get_active_checkins()
        for c in checkins:
            self.tree.insert("", "end", iid=str(c["id"]), values=(
                c["id"],
                c["guest_name"],
                c["room_number"],
                c["room_type"],
                format_currency(c["price_per_night"]),
                c["check_in_date"]
            ))

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        checkin_id = int(selected[0])
        checkins = self.db.get_active_checkins()
        matched = [c for c in checkins if c["id"] == checkin_id]

        if matched:
            c = matched[0]
            self.current_checkin = c

            self.lbl_id.config(text=str(c["id"]))
            self.lbl_guest.config(text=c["guest_name"])
            self.lbl_room.config(text=f"{c['room_number']} ({c['room_type']})")
            self.lbl_checkin_date.config(text=c["check_in_date"])

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.ent_checkout_date.delete(0, tk.END)
            self.ent_checkout_date.insert(0, now_str)

            self.calculate_bill()

    def clear_form(self):
        self.current_checkin = None
        self.calc_data = {}
        self.lbl_id.config(text="-")
        self.lbl_guest.config(text="-")
        self.lbl_room.config(text="-")
        self.lbl_checkin_date.config(text="-")
        self.ent_checkout_date.delete(0, tk.END)
        self.lbl_nights.config(text="0")
        self.lbl_room_charges.config(text="$0.00")
        self.lbl_service_charges.config(text="$0.00")
        self.lbl_grand_total.config(text="$0.00")

    def calculate_bill(self):
        if not self.current_checkin:
            return

        c = self.current_checkin
        checkout_str = self.ent_checkout_date.get().strip()

        nights = calculate_nights(c["check_in_date"], checkout_str)
        room_rate = c["price_per_night"]
        room_charges = nights * room_rate

        service_charges = self.db.get_total_services_amount(c["id"])

        tax_rate_str = self.ent_tax_rate.get().strip()
        discount_str = self.ent_discount.get().strip()

        tax_rate = float(tax_rate_str) if validate_positive_number(tax_rate_str, allow_zero=True) else 10.0
        discount = float(discount_str) if validate_positive_number(discount_str, allow_zero=True) else 0.0

        subtotal = room_charges + service_charges
        tax_amount = (subtotal - discount) * (tax_rate / 100.0)
        tax_amount = max(0.0, tax_amount)
        grand_total = max(0.0, subtotal - discount + tax_amount)

        self.lbl_nights.config(text=str(nights))
        self.lbl_room_charges.config(text=format_currency(room_charges))
        self.lbl_service_charges.config(text=format_currency(service_charges))
        self.lbl_grand_total.config(text=format_currency(grand_total))

        self.calc_data = {
            "checkout_datetime": checkout_str,
            "total_nights": nights,
            "room_charges": room_charges,
            "service_charges": service_charges,
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "discount": discount,
            "grand_total": grand_total
        }

    def perform_checkout(self):
        if not self.current_checkin:
            messagebox.showwarning("Select Error", "Please select an active occupant to check out.", parent=self)
            return

        self.calculate_bill()

        checkin_id = self.current_checkin["id"]
        room_num = self.current_checkin["room_number"]
        guest_name = self.current_checkin["guest_name"]

        confirm_msg = f"Confirm Checkout & Settlement for {guest_name} (Room {room_num})?\nGrand Total: {format_currency(self.calc_data['grand_total'])}"
        if messagebox.askyesno("Confirm Check-Out", confirm_msg, parent=self):
            try:
                checkout_id, bill_num = self.db.process_checkout(
                    checkin_id=checkin_id,
                    checkout_datetime=self.calc_data["checkout_datetime"],
                    total_nights=self.calc_data["total_nights"],
                    room_charges=self.calc_data["room_charges"],
                    service_charges=self.calc_data["service_charges"],
                    tax_rate=self.calc_data["tax_rate"],
                    tax_amount=self.calc_data["tax_amount"],
                    discount=self.calc_data["discount"],
                    grand_total=self.calc_data["grand_total"]
                )

                messagebox.showinfo("Success", f"Guest successfully checked out!\nBill Number: {bill_num}", parent=self)
                self.load_active_checkins()
            except Exception as e:
                messagebox.showerror("Checkout Error", f"Failed to process checkout: {e}", parent=self)
