import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from utils import format_currency

class CheckInFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        self._build_ui()
        self.load_initial_data()

    def _build_ui(self):
        # Header / Title Frame
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Guest Check-In System", font=("Helvetica", 16, "bold"), foreground="#2C3E50").pack(side="left")

        btn_refresh = ttk.Button(header, text="Reset / Refresh", command=self.load_initial_data)
        btn_refresh.pack(side="right")

        main_paned = ttk.PanedWindow(self, orient="horizontal")
        main_paned.pack(fill="both", expand=True)

        # --- Left Form Frame ---
        form_frame = ttk.LabelFrame(main_paned, text=" New Check-In ", padding="15 15 15 15")
        main_paned.add(form_frame, weight=1)

        # Optional Reservation Link
        ttk.Label(form_frame, text="Link Reservation (Optional):").grid(row=0, column=0, sticky="w", pady=5)
        self.cbo_res = ttk.Combobox(form_frame, state="readonly", width=22)
        self.cbo_res.grid(row=0, column=1, sticky="w", pady=5)
        self.cbo_res.bind("<<ComboboxSelected>>", self.on_reservation_select)

        # Guest Selector
        ttk.Label(form_frame, text="Guest:*").grid(row=1, column=0, sticky="w", pady=5)
        self.cbo_guest = ttk.Combobox(form_frame, state="readonly", width=22)
        self.cbo_guest.grid(row=1, column=1, sticky="w", pady=5)

        # Available Room Selector
        ttk.Label(form_frame, text="Available Room:*").grid(row=2, column=0, sticky="w", pady=5)
        self.cbo_room = ttk.Combobox(form_frame, state="readonly", width=22)
        self.cbo_room.grid(row=2, column=1, sticky="w", pady=5)

        # Check-in Time (Read-only / Current)
        ttk.Label(form_frame, text="Check-In Time:").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_checkin_time = ttk.Entry(form_frame, width=24)
        self.ent_checkin_time.grid(row=3, column=1, sticky="w", pady=5)

        # Expected Check-out Date
        ttk.Label(form_frame, text="Expected Check-Out:").grid(row=4, column=0, sticky="w", pady=5)
        self.ent_exp_checkout = ttk.Entry(form_frame, width=24)
        self.ent_exp_checkout.grid(row=4, column=1, sticky="w", pady=5)

        # Action Buttons
        btn_box = ttk.Frame(form_frame)
        btn_box.grid(row=5, column=0, columnspan=2, pady=(20, 0), sticky="ew")

        btn_checkin = ttk.Button(btn_box, text="Confirm Check-In 🔑", command=self.perform_checkin)
        btn_checkin.pack(side="left", expand=True, fill="x", padx=2)

        btn_clear = ttk.Button(btn_box, text="Clear", command=self.clear_form)
        btn_clear.pack(side="left", expand=True, fill="x", padx=2)

        # --- Right Table Frame (Active Check-ins) ---
        table_frame = ttk.LabelFrame(main_paned, text=" Currently Active Occupants ", padding="10 10 10 10")
        main_paned.add(table_frame, weight=3)

        columns = ("id", "guest_name", "room_number", "room_type", "price", "check_in_date", "expected_check_out")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="Check-In ID")
        self.tree.heading("guest_name", text="Guest Name")
        self.tree.heading("room_number", text="Room No.")
        self.tree.heading("room_type", text="Room Type")
        self.tree.heading("price", text="Price / Night")
        self.tree.heading("check_in_date", text="Check-In Time")
        self.tree.heading("expected_check_out", text="Expected Out")

        self.tree.column("id", width=80, anchor="center")
        self.tree.column("guest_name", width=140, anchor="w")
        self.tree.column("room_number", width=80, anchor="center")
        self.tree.column("room_type", width=100, anchor="center")
        self.tree.column("price", width=90, anchor="e")
        self.tree.column("check_in_date", width=140, anchor="center")
        self.tree.column("expected_check_out", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_initial_data(self):
        self._load_comboboxes()
        self.clear_form()
        self.load_active_checkins()

    def _load_comboboxes(self):
        # Guests
        guests = self.db.get_all_guests()
        self.guest_dict = {f"{g['id']} - {g['full_name']}": g['id'] for g in guests}
        self.cbo_guest['values'] = list(self.guest_dict.keys())

        # Available Rooms (or Reserved rooms that can be checked in)
        rooms = self.db.get_all_rooms()
        available_rooms = [r for r in rooms if r['status'] in ('Available', 'Reserved')]
        self.cbo_room['values'] = [f"{r['room_number']} ({r['room_type']} - ${r['price_per_night']:.2f})" for r in available_rooms]

        # Active Reservations
        reservations = self.db.get_all_reservations()
        active_res = [r for r in reservations if r['status'] == 'Reserved']
        self.res_dict = {f"Res #{r['id']} - {r['guest_name']} (Room {r['room_number']})": r for r in active_res}
        self.cbo_res['values'] = ["None"] + list(self.res_dict.keys())
        self.cbo_res.current(0)

    def load_active_checkins(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        checkins = self.db.get_active_checkins()
        for c in checkins:
            self.tree.insert("", "end", iid=str(c["id"]), values=(
                c["id"],
                c["guest_name"],
                c["room_number"],
                c["room_type"],
                format_currency(c["price_per_night"]),
                c["check_in_date"],
                c["expected_check_out"]
            ))

    def on_reservation_select(self, event):
        sel = self.cbo_res.get()
        if sel in self.res_dict:
            res = self.res_dict[sel]

            # Set Guest
            for key in self.cbo_guest['values']:
                if key.startswith(f"{res['guest_id']} -"):
                    self.cbo_guest.set(key)
                    break

            # Set Room
            for key in self.cbo_room['values']:
                if key.startswith(str(res['room_number'])):
                    self.cbo_room.set(key)
                    break

            self.ent_exp_checkout.delete(0, tk.END)
            self.ent_exp_checkout.insert(0, res['check_out_date'])

    def clear_form(self):
        self.cbo_res.current(0)
        if self.cbo_guest['values']:
            self.cbo_guest.current(0)
        if self.cbo_room['values']:
            self.cbo_room.current(0)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        exp_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

        self.ent_checkin_time.delete(0, tk.END)
        self.ent_checkin_time.insert(0, now_str)

        self.ent_exp_checkout.delete(0, tk.END)
        self.ent_exp_checkout.insert(0, exp_str)

    def perform_checkin(self):
        guest_sel = self.cbo_guest.get()
        room_sel = self.cbo_room.get()
        checkin_time = self.ent_checkin_time.get().strip()
        exp_checkout = self.ent_exp_checkout.get().strip()
        res_sel = self.cbo_res.get()

        if not guest_sel or guest_sel not in self.guest_dict:
            messagebox.showwarning("Validation Error", "Please select a guest.", parent=self)
            return

        if not room_sel:
            messagebox.showwarning("Validation Error", "Please select a room.", parent=self)
            return

        guest_id = self.guest_dict[guest_sel]
        room_num = room_sel.split()[0]
        res_id = self.res_dict[res_sel]["id"] if res_sel in self.res_dict else None

        try:
            checkin_id = self.db.check_in_guest(guest_id, room_num, checkin_time, exp_checkout, res_id)
            messagebox.showinfo("Success", f"Guest checked into Room {room_num} successfully! (Check-In ID: {checkin_id})", parent=self)
            self.load_initial_data()
        except Exception as e:
            messagebox.showerror("Check-In Error", f"Could not perform check-in: {e}", parent=self)
