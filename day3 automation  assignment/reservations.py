import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from utils import validate_date

class ReservationsFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        self._build_ui()
        self.load_initial_data()

    def _build_ui(self):
        # Header / Title Frame
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Reservation Management", font=("Helvetica", 16, "bold"), foreground="#2C3E50").pack(side="left")

        # Top Search Bar
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Search Reservation:").pack(side="left", padx=(0, 5))
        self.ent_search = ttk.Entry(search_frame, width=25)
        self.ent_search.pack(side="left", padx=(0, 5))
        self.ent_search.bind("<Return>", lambda e: self.search_reservations())

        btn_search = ttk.Button(search_frame, text="Search", command=self.search_reservations)
        btn_search.pack(side="left", padx=(0, 5))

        btn_refresh = ttk.Button(search_frame, text="Reset / Refresh", command=self.load_initial_data)
        btn_refresh.pack(side="left")

        # Main Paned Area
        main_paned = ttk.PanedWindow(self, orient="horizontal")
        main_paned.pack(fill="both", expand=True)

        # --- Left Form Frame ---
        form_frame = ttk.LabelFrame(main_paned, text=" Reservation Details ", padding="15 15 15 15")
        main_paned.add(form_frame, weight=1)

        # Reservation ID (Read-only)
        ttk.Label(form_frame, text="Reservation ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_res_id = ttk.Entry(form_frame, width=22, state="disabled")
        self.ent_res_id.grid(row=0, column=1, sticky="w", pady=5)

        # Guest Selector
        ttk.Label(form_frame, text="Select Guest:").grid(row=1, column=0, sticky="w", pady=5)
        self.cbo_guest = ttk.Combobox(form_frame, state="readonly", width=20)
        self.cbo_guest.grid(row=1, column=1, sticky="w", pady=5)

        # Room Selector
        ttk.Label(form_frame, text="Select Room:").grid(row=2, column=0, sticky="w", pady=5)
        self.cbo_room = ttk.Combobox(form_frame, state="readonly", width=20)
        self.cbo_room.grid(row=2, column=1, sticky="w", pady=5)

        # Check-in Date
        ttk.Label(form_frame, text="Check-in Date (YYYY-MM-DD):").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_checkin = ttk.Entry(form_frame, width=22)
        self.ent_checkin.grid(row=3, column=1, sticky="w", pady=5)

        # Check-out Date
        ttk.Label(form_frame, text="Check-out Date (YYYY-MM-DD):").grid(row=4, column=0, sticky="w", pady=5)
        self.ent_checkout = ttk.Entry(form_frame, width=22)
        self.ent_checkout.grid(row=4, column=1, sticky="w", pady=5)

        # Guests Count
        ttk.Label(form_frame, text="No. of Guests:").grid(row=5, column=0, sticky="w", pady=5)
        self.spn_guests = ttk.Spinbox(form_frame, from_=1, to=10, width=20)
        self.spn_guests.grid(row=5, column=1, sticky="w", pady=5)
        self.spn_guests.set(1)

        # Status
        ttk.Label(form_frame, text="Status:").grid(row=6, column=0, sticky="w", pady=5)
        self.cbo_status = ttk.Combobox(form_frame, values=["Reserved", "Checked-In", "Cancelled", "Completed"], state="readonly", width=20)
        self.cbo_status.grid(row=6, column=1, sticky="w", pady=5)
        self.cbo_status.current(0)

        # Action Buttons
        btn_box = ttk.Frame(form_frame)
        btn_box.grid(row=7, column=0, columnspan=2, pady=(20, 0), sticky="ew")

        btn_create = ttk.Button(btn_box, text="Create", command=self.create_reservation)
        btn_create.pack(side="left", expand=True, fill="x", padx=2)

        btn_update = ttk.Button(btn_box, text="Update", command=self.update_reservation)
        btn_update.pack(side="left", expand=True, fill="x", padx=2)

        btn_cancel = ttk.Button(btn_box, text="Cancel Res.", command=self.cancel_reservation)
        btn_cancel.pack(side="left", expand=True, fill="x", padx=2)

        btn_clear = ttk.Button(btn_box, text="Clear", command=self.clear_form)
        btn_clear.pack(side="left", expand=True, fill="x", padx=2)

        # --- Right Table Frame ---
        table_frame = ttk.Frame(main_paned)
        main_paned.add(table_frame, weight=3)

        columns = ("id", "guest_name", "room_number", "check_in_date", "check_out_date", "num_guests", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="Res ID")
        self.tree.heading("guest_name", text="Guest Name")
        self.tree.heading("room_number", text="Room No.")
        self.tree.heading("check_in_date", text="Check-In")
        self.tree.heading("check_out_date", text="Check-Out")
        self.tree.heading("num_guests", text="Guests")
        self.tree.heading("status", text="Status")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("guest_name", width=140, anchor="w")
        self.tree.column("room_number", width=80, anchor="center")
        self.tree.column("check_in_date", width=100, anchor="center")
        self.tree.column("check_out_date", width=100, anchor="center")
        self.tree.column("num_guests", width=60, anchor="center")
        self.tree.column("status", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def load_initial_data(self):
        self.clear_form()
        self._load_combobox_data()
        self.load_reservations()

    def _load_combobox_data(self):
        # Guests combobox
        guests = self.db.get_all_guests()
        self.guest_dict = {f"{g['id']} - {g['full_name']} ({g['phone']})": g['id'] for g in guests}
        self.cbo_guest['values'] = list(self.guest_dict.keys())
        if self.cbo_guest['values']:
            self.cbo_guest.current(0)

        # Rooms combobox
        rooms = self.db.get_all_rooms()
        self.cbo_room['values'] = [f"{r['room_number']} ({r['room_type']})" for r in rooms]
        if self.cbo_room['values']:
            self.cbo_room.current(0)

    def load_reservations(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        res_list = self.db.get_all_reservations()
        for r in res_list:
            self.tree.insert("", "end", iid=str(r["id"]), values=(
                r["id"],
                r["guest_name"],
                r["room_number"],
                r["check_in_date"],
                r["check_out_date"],
                r["num_guests"],
                r["status"]
            ))

    def search_reservations(self):
        term = self.ent_search.get().strip()
        if not term:
            self.load_reservations()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        res_list = self.db.search_reservations(term)
        for r in res_list:
            self.tree.insert("", "end", iid=str(r["id"]), values=(
                r["id"],
                r["guest_name"],
                r["room_number"],
                r["check_in_date"],
                r["check_out_date"],
                r["num_guests"],
                r["status"]
            ))

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item["values"]

        self.ent_res_id.config(state="normal")
        self.ent_res_id.delete(0, tk.END)
        self.ent_res_id.insert(0, values[0])
        self.ent_res_id.config(state="disabled")

        # Select matching guest in dropdown
        target_name = values[1]
        for key in self.cbo_guest['values']:
            if target_name in key:
                self.cbo_guest.set(key)
                break

        # Select matching room in dropdown
        target_room = str(values[2])
        for key in self.cbo_room['values']:
            if key.startswith(target_room):
                self.cbo_room.set(key)
                break

        self.ent_checkin.delete(0, tk.END)
        self.ent_checkin.insert(0, values[3])

        self.ent_checkout.delete(0, tk.END)
        self.ent_checkout.insert(0, values[4])

        self.spn_guests.set(values[5])
        self.cbo_status.set(values[6])

    def clear_form(self):
        self.ent_res_id.config(state="normal")
        self.ent_res_id.delete(0, tk.END)
        self.ent_res_id.config(state="disabled")

        today_str = date.today().strftime("%Y-%m-%d")
        tomorrow_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

        self.ent_checkin.delete(0, tk.END)
        self.ent_checkin.insert(0, today_str)

        self.ent_checkout.delete(0, tk.END)
        self.ent_checkout.insert(0, tomorrow_str)

        self.spn_guests.set(1)
        self.cbo_status.current(0)
        self.ent_search.delete(0, tk.END)

    def create_reservation(self):
        guest_sel = self.cbo_guest.get().strip()
        room_sel = self.cbo_room.get().strip()
        checkin_date = self.ent_checkin.get().strip()
        checkout_date = self.ent_checkout.get().strip()
        num_guests = self.spn_guests.get().strip()

        if not guest_sel or guest_sel not in self.guest_dict:
            messagebox.showwarning("Validation Error", "Please select a valid guest.", parent=self)
            return

        if not room_sel:
            messagebox.showwarning("Validation Error", "Please select a room.", parent=self)
            return

        if not validate_date(checkin_date) or not validate_date(checkout_date):
            messagebox.showwarning("Validation Error", "Please enter valid dates in YYYY-MM-DD format.", parent=self)
            return

        if checkin_date >= checkout_date:
            messagebox.showwarning("Validation Error", "Check-out date must be after check-in date.", parent=self)
            return

        guest_id = self.guest_dict[guest_sel]
        room_num = room_sel.split()[0]

        try:
            res_id = self.db.create_reservation(guest_id, room_num, checkin_date, checkout_date, int(num_guests))
            messagebox.showinfo("Success", f"Reservation #{res_id} created successfully!", parent=self)
            self.load_initial_data()
        except Exception as e:
            messagebox.showerror("Booking Error", f"Cannot create reservation: {e}", parent=self)

    def update_reservation(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Please select a reservation to update.", parent=self)
            return

        res_id = selected[0]
        guest_sel = self.cbo_guest.get().strip()
        room_sel = self.cbo_room.get().strip()
        checkin_date = self.ent_checkin.get().strip()
        checkout_date = self.ent_checkout.get().strip()
        num_guests = self.spn_guests.get().strip()
        status = self.cbo_status.get().strip()

        if not guest_sel or guest_sel not in self.guest_dict or not room_sel:
            messagebox.showwarning("Validation Error", "Please select valid guest and room.", parent=self)
            return

        if not validate_date(checkin_date) or not validate_date(checkout_date) or checkin_date >= checkout_date:
            messagebox.showwarning("Validation Error", "Invalid date selection.", parent=self)
            return

        guest_id = self.guest_dict[guest_sel]
        room_num = room_sel.split()[0]

        try:
            self.db.update_reservation(res_id, guest_id, room_num, checkin_date, checkout_date, int(num_guests), status)
            messagebox.showinfo("Success", f"Reservation #{res_id} updated successfully!", parent=self)
            self.load_initial_data()
        except Exception as e:
            messagebox.showerror("Error", f"Could not update reservation: {e}", parent=self)

    def cancel_reservation(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Please select a reservation to cancel.", parent=self)
            return

        res_id = selected[0]
        if messagebox.askyesno("Confirm Cancel", f"Are you sure you want to cancel Reservation #{res_id}?", parent=self):
            try:
                self.db.cancel_reservation(res_id)
                messagebox.showinfo("Success", f"Reservation #{res_id} cancelled successfully!", parent=self)
                self.load_initial_data()
            except Exception as e:
                messagebox.showerror("Error", f"Could not cancel reservation: {e}", parent=self)
