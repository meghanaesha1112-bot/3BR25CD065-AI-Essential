import tkinter as tk
from tkinter import ttk, messagebox
from utils import validate_phone, validate_email, validate_positive_number

class GuestsFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        self._build_ui()
        self.load_guests()

    def _build_ui(self):
        # Header / Title Frame
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Guest Management", font=("Helvetica", 16, "bold"), foreground="#2C3E50").pack(side="left")

        # Top Control Bar (Search)
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Search Guest:").pack(side="left", padx=(0, 5))
        self.ent_search = ttk.Entry(search_frame, width=25)
        self.ent_search.pack(side="left", padx=(0, 5))
        self.ent_search.bind("<Return>", lambda e: self.search_guests())

        btn_search = ttk.Button(search_frame, text="Search", command=self.search_guests)
        btn_search.pack(side="left", padx=(0, 5))

        btn_refresh = ttk.Button(search_frame, text="Reset / Refresh", command=self.load_guests)
        btn_refresh.pack(side="left")

        # Main Paned Area
        main_paned = ttk.PanedWindow(self, orient="horizontal")
        main_paned.pack(fill="both", expand=True)

        # --- Left Form Frame ---
        form_frame = ttk.LabelFrame(main_paned, text=" Guest Details ", padding="15 15 15 15")
        main_paned.add(form_frame, weight=1)

        # Guest ID (Read-only)
        ttk.Label(form_frame, text="Guest ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_id = ttk.Entry(form_frame, width=22, state="disabled")
        self.ent_id.grid(row=0, column=1, sticky="w", pady=5)

        # Full Name
        ttk.Label(form_frame, text="Full Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_name = ttk.Entry(form_frame, width=22)
        self.ent_name.grid(row=1, column=1, sticky="w", pady=5)

        # Phone Number
        ttk.Label(form_frame, text="Phone Number:").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_phone = ttk.Entry(form_frame, width=22)
        self.ent_phone.grid(row=2, column=1, sticky="w", pady=5)

        # Email
        ttk.Label(form_frame, text="Email:").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_email = ttk.Entry(form_frame, width=22)
        self.ent_email.grid(row=3, column=1, sticky="w", pady=5)

        # Address
        ttk.Label(form_frame, text="Address:").grid(row=4, column=0, sticky="w", pady=5)
        self.ent_address = ttk.Entry(form_frame, width=22)
        self.ent_address.grid(row=4, column=1, sticky="w", pady=5)

        # Govt ID
        ttk.Label(form_frame, text="Govt ID / Passport:").grid(row=5, column=0, sticky="w", pady=5)
        self.ent_govt_id = ttk.Entry(form_frame, width=22)
        self.ent_govt_id.grid(row=5, column=1, sticky="w", pady=5)

        # Number of Guests
        ttk.Label(form_frame, text="No. of Guests:").grid(row=6, column=0, sticky="w", pady=5)
        self.spn_guests = ttk.Spinbox(form_frame, from_=1, to=10, width=20)
        self.spn_guests.grid(row=6, column=1, sticky="w", pady=5)
        self.spn_guests.set(1)

        # Action Buttons
        btn_box = ttk.Frame(form_frame)
        btn_box.grid(row=7, column=0, columnspan=2, pady=(20, 0), sticky="ew")

        btn_add = ttk.Button(btn_box, text="Add Guest", command=self.add_guest)
        btn_add.pack(side="left", expand=True, fill="x", padx=2)

        btn_update = ttk.Button(btn_box, text="Update", command=self.update_guest)
        btn_update.pack(side="left", expand=True, fill="x", padx=2)

        btn_delete = ttk.Button(btn_box, text="Delete", command=self.delete_guest)
        btn_delete.pack(side="left", expand=True, fill="x", padx=2)

        btn_clear = ttk.Button(btn_box, text="Clear", command=self.clear_form)
        btn_clear.pack(side="left", expand=True, fill="x", padx=2)

        # --- Right Table Frame ---
        table_frame = ttk.Frame(main_paned)
        main_paned.add(table_frame, weight=3)

        columns = ("id", "full_name", "phone", "email", "address", "govt_id", "num_guests")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("full_name", text="Full Name")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("email", text="Email")
        self.tree.heading("address", text="Address")
        self.tree.heading("govt_id", text="Govt ID")
        self.tree.heading("num_guests", text="Guests")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("full_name", width=140, anchor="w")
        self.tree.column("phone", width=110, anchor="center")
        self.tree.column("email", width=140, anchor="w")
        self.tree.column("address", width=140, anchor="w")
        self.tree.column("govt_id", width=100, anchor="center")
        self.tree.column("num_guests", width=60, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def load_guests(self):
        self.clear_form()
        for item in self.tree.get_children():
            self.tree.delete(item)

        guests = self.db.get_all_guests()
        for g in guests:
            self.tree.insert("", "end", iid=str(g["id"]), values=(
                g["id"],
                g["full_name"],
                g["phone"],
                g["email"] or "",
                g["address"] or "",
                g["govt_id"],
                g["num_guests"]
            ))

    def search_guests(self):
        term = self.ent_search.get().strip()
        if not term:
            self.load_guests()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        guests = self.db.search_guests(term)
        for g in guests:
            self.tree.insert("", "end", iid=str(g["id"]), values=(
                g["id"],
                g["full_name"],
                g["phone"],
                g["email"] or "",
                g["address"] or "",
                g["govt_id"],
                g["num_guests"]
            ))

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item["values"]

        self.ent_id.config(state="normal")
        self.ent_id.delete(0, tk.END)
        self.ent_id.insert(0, values[0])
        self.ent_id.config(state="disabled")

        self.ent_name.delete(0, tk.END)
        self.ent_name.insert(0, values[1])

        self.ent_phone.delete(0, tk.END)
        self.ent_phone.insert(0, values[2])

        self.ent_email.delete(0, tk.END)
        self.ent_email.insert(0, values[3])

        self.ent_address.delete(0, tk.END)
        self.ent_address.insert(0, values[4])

        self.ent_govt_id.delete(0, tk.END)
        self.ent_govt_id.insert(0, values[5])

        self.spn_guests.set(values[6])

    def clear_form(self):
        self.ent_id.config(state="normal")
        self.ent_id.delete(0, tk.END)
        self.ent_id.config(state="disabled")

        self.ent_name.delete(0, tk.END)
        self.ent_phone.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.ent_address.delete(0, tk.END)
        self.ent_govt_id.delete(0, tk.END)
        self.spn_guests.set(1)
        self.ent_search.delete(0, tk.END)

    def add_guest(self):
        name = self.ent_name.get().strip()
        phone = self.ent_phone.get().strip()
        email = self.ent_email.get().strip()
        address = self.ent_address.get().strip()
        govt_id = self.ent_govt_id.get().strip()
        num_guests = self.spn_guests.get().strip()

        if not name:
            messagebox.showwarning("Validation Error", "Please enter guest full name.", parent=self)
            return

        if not validate_phone(phone):
            messagebox.showwarning("Validation Error", "Please enter a valid phone number (at least 7 digits).", parent=self)
            return

        if email and not validate_email(email):
            messagebox.showwarning("Validation Error", "Please enter a valid email address.", parent=self)
            return

        if not govt_id:
            messagebox.showwarning("Validation Error", "Please enter Government ID / Passport number.", parent=self)
            return

        try:
            guest_id = self.db.add_guest(name, phone, email, address, govt_id, int(num_guests))
            messagebox.showinfo("Success", f"Guest '{name}' added successfully (ID: {guest_id})!", parent=self)
            self.load_guests()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add guest: {e}", parent=self)

    def update_guest(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Please select a guest to update.", parent=self)
            return

        guest_id = selected[0]
        name = self.ent_name.get().strip()
        phone = self.ent_phone.get().strip()
        email = self.ent_email.get().strip()
        address = self.ent_address.get().strip()
        govt_id = self.ent_govt_id.get().strip()
        num_guests = self.spn_guests.get().strip()

        if not name or not validate_phone(phone) or not govt_id:
            messagebox.showwarning("Validation Error", "Please fill in required fields (Name, Phone, Govt ID).", parent=self)
            return

        if email and not validate_email(email):
            messagebox.showwarning("Validation Error", "Please enter a valid email address.", parent=self)
            return

        try:
            self.db.update_guest(guest_id, name, phone, email, address, govt_id, int(num_guests))
            messagebox.showinfo("Success", f"Guest ID {guest_id} updated successfully!", parent=self)
            self.load_guests()
        except Exception as e:
            messagebox.showerror("Error", f"Could not update guest: {e}", parent=self)

    def delete_guest(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Please select a guest to delete.", parent=self)
            return

        guest_id = selected[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Guest ID {guest_id}?", parent=self):
            try:
                self.db.delete_guest(guest_id)
                messagebox.showinfo("Success", f"Guest ID {guest_id} deleted successfully!", parent=self)
                self.load_guests()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete guest: {e}", parent=self)
