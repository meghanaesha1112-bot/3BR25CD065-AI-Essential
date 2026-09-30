import tkinter as tk
from tkinter import ttk, messagebox
from utils import format_currency, validate_positive_number

class ServicesFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        self._build_ui()
        self.load_active_checkins()

    def _build_ui(self):
        # Header / Title Frame
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Additional Services & Room Charges", font=("Helvetica", 16, "bold"), foreground="#2C3E50").pack(side="left")

        btn_refresh = ttk.Button(header, text="Reset / Refresh", command=self.load_active_checkins)
        btn_refresh.pack(side="right")

        main_paned = ttk.PanedWindow(self, orient="horizontal")
        main_paned.pack(fill="both", expand=True)

        # --- Left Frame: Select Occupant & Add Charge Form ---
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        # Occupant Selection List/Box
        occ_group = ttk.LabelFrame(left_frame, text=" Select Active Guest ", padding="10 10 10 10")
        occ_group.pack(fill="x", pady=(0, 10))

        ttk.Label(occ_group, text="Occupant:").pack(anchor="w")
        self.cbo_occupants = ttk.Combobox(occ_group, state="readonly", width=30)
        self.cbo_occupants.pack(fill="x", pady=5)
        self.cbo_occupants.bind("<<ComboboxSelected>>", self.on_occupant_select)

        # Service Entry Form
        form_group = ttk.LabelFrame(left_frame, text=" Add New Service Charge ", padding="10 10 10 10")
        form_group.pack(fill="both", expand=True)

        ttk.Label(form_group, text="Service Category:").grid(row=0, column=0, sticky="w", pady=5)
        self.cbo_preset = ttk.Combobox(form_group, values=["Food & Beverage", "Laundry", "Room Service", "Transport", "Spa & Wellness", "Custom Service"], state="readonly", width=20)
        self.cbo_preset.grid(row=0, column=1, sticky="w", pady=5)
        self.cbo_preset.current(0)
        self.cbo_preset.bind("<<ComboboxSelected>>", self.on_preset_select)

        ttk.Label(form_group, text="Service Item Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_service_name = ttk.Entry(form_group, width=22)
        self.ent_service_name.grid(row=1, column=1, sticky="w", pady=5)
        self.ent_service_name.insert(0, "Breakfast Buffet")

        ttk.Label(form_group, text="Quantity:").grid(row=2, column=0, sticky="w", pady=5)
        self.spn_qty = ttk.Spinbox(form_group, from_=1, to=50, width=20)
        self.spn_qty.grid(row=2, column=1, sticky="w", pady=5)
        self.spn_qty.set(1)

        ttk.Label(form_group, text="Price per Unit ($):").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_price = ttk.Entry(form_group, width=22)
        self.ent_price.grid(row=3, column=1, sticky="w", pady=5)
        self.ent_price.insert(0, "15.00")

        # Add Service Button
        btn_add = ttk.Button(form_group, text="Add Service Charge 🛎️", command=self.add_service)
        btn_add.grid(row=4, column=0, columnspan=2, pady=(15, 0), sticky="ew")

        # --- Right Frame: Services Logged for Selected Occupant ---
        right_frame = ttk.LabelFrame(main_paned, text=" Logged Charges for Selected Guest ", padding="10 10 10 10")
        main_paned.add(right_frame, weight=2)

        columns = ("id", "service_name", "quantity", "price", "total_amount", "created_at")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("service_name", text="Service Name")
        self.tree.heading("quantity", text="Qty")
        self.tree.heading("price", text="Unit Price")
        self.tree.heading("total_amount", text="Total")
        self.tree.heading("created_at", text="Logged Time")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("service_name", width=140, anchor="w")
        self.tree.column("quantity", width=50, anchor="center")
        self.tree.column("price", width=80, anchor="e")
        self.tree.column("total_amount", width=90, anchor="e")
        self.tree.column("created_at", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bottom Total Summary & Action bar
        summary_bar = ttk.Frame(right_frame, padding="5 10 5 0")
        summary_bar.pack(side="bottom", fill="x")

        ttk.Label(summary_bar, text="Total Service Charges:", font=("Helvetica", 11, "bold")).pack(side="left")
        self.lbl_total_services = ttk.Label(summary_bar, text="$0.00", font=("Helvetica", 12, "bold"), foreground="#E67E22")
        self.lbl_total_services.pack(side="left", padx=10)

        btn_delete_svc = ttk.Button(summary_bar, text="Remove Selected Charge", command=self.delete_service)
        btn_delete_svc.pack(side="right")

        self.occupant_dict = {}

    def load_active_checkins(self):
        checkins = self.db.get_active_checkins()
        self.occupant_dict = {f"Room {c['room_number']} - {c['guest_name']} (CheckIn #{c['id']})": c['id'] for c in checkins}

        vals = list(self.occupant_dict.keys())
        self.cbo_occupants['values'] = vals
        if vals:
            self.cbo_occupants.current(0)
            self.load_logged_services()
        else:
            self.cbo_occupants.set("")
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.lbl_total_services.config(text="$0.00")

    def on_preset_select(self, event):
        preset = self.cbo_preset.get()
        if preset == "Food & Beverage":
            self.ent_service_name.delete(0, tk.END)
            self.ent_service_name.insert(0, "Breakfast Buffet")
            self.ent_price.delete(0, tk.END)
            self.ent_price.insert(0, "15.00")
        elif preset == "Laundry":
            self.ent_service_name.delete(0, tk.END)
            self.ent_service_name.insert(0, "Laundry Service")
            self.ent_price.delete(0, tk.END)
            self.ent_price.insert(0, "10.00")
        elif preset == "Room Service":
            self.ent_service_name.delete(0, tk.END)
            self.ent_service_name.insert(0, "In-Room Dining")
            self.ent_price.delete(0, tk.END)
            self.ent_price.insert(0, "25.00")
        elif preset == "Transport":
            self.ent_service_name.delete(0, tk.END)
            self.ent_service_name.insert(0, "Airport Shuttle")
            self.ent_price.delete(0, tk.END)
            self.ent_price.insert(0, "35.00")
        elif preset == "Spa & Wellness":
            self.ent_service_name.delete(0, tk.END)
            self.ent_service_name.insert(0, "Spa Treatment")
            self.ent_price.delete(0, tk.END)
            self.ent_price.insert(0, "60.00")

    def on_occupant_select(self, event):
        self.load_logged_services()

    def load_logged_services(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        sel = self.cbo_occupants.get()
        if not sel or sel not in self.occupant_dict:
            self.lbl_total_services.config(text="$0.00")
            return

        checkin_id = self.occupant_dict[sel]
        services = self.db.get_services_for_checkin(checkin_id)

        total = 0.0
        for s in services:
            total += s["total_amount"]
            self.tree.insert("", "end", iid=str(s["id"]), values=(
                s["id"],
                s["service_name"],
                s["quantity"],
                format_currency(s["price"]),
                format_currency(s["total_amount"]),
                s["created_at"]
            ))

        self.lbl_total_services.config(text=format_currency(total))

    def add_service(self):
        sel = self.cbo_occupants.get()
        if not sel or sel not in self.occupant_dict:
            messagebox.showwarning("Selection Error", "Please select an active occupant.", parent=self)
            return

        checkin_id = self.occupant_dict[sel]
        s_name = self.ent_service_name.get().strip()
        qty_str = self.spn_qty.get().strip()
        price_str = self.ent_price.get().strip()

        if not s_name:
            messagebox.showwarning("Validation Error", "Please enter a service name.", parent=self)
            return

        if not validate_positive_number(price_str, allow_zero=True):
            messagebox.showwarning("Validation Error", "Please enter a valid price.", parent=self)
            return

        try:
            self.db.add_service_charge(checkin_id, s_name, int(qty_str), float(price_str))
            messagebox.showinfo("Success", f"Service charge '{s_name}' added successfully!", parent=self)
            self.load_logged_services()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add service charge: {e}", parent=self)

    def delete_service(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Please select a service charge to remove.", parent=self)
            return

        service_id = selected[0]
        if messagebox.askyesno("Confirm Delete", "Remove this service charge?", parent=self):
            try:
                self.db.delete_service_charge(service_id)
                self.load_logged_services()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete charge: {e}", parent=self)
