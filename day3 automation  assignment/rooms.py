import tkinter as tk
from tkinter import ttk, messagebox
from utils import validate_positive_number, format_currency

class RoomsFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        self._build_ui()
        self.load_rooms()

    def _build_ui(self):
        # Header / Title Frame
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Room Management", font=("Helvetica", 16, "bold"), foreground="#2C3E50").pack(side="left")

        # Top Control Bar (Search & Filter)
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Search Room:").pack(side="left", padx=(0, 5))
        self.ent_search = ttk.Entry(search_frame, width=25)
        self.ent_search.pack(side="left", padx=(0, 5))
        self.ent_search.bind("<Return>", lambda e: self.search_rooms())

        btn_search = ttk.Button(search_frame, text="Search", command=self.search_rooms)
        btn_search.pack(side="left", padx=(0, 5))

        btn_refresh = ttk.Button(search_frame, text="Reset / Refresh", command=self.load_rooms)
        btn_refresh.pack(side="left")

        # Content Area: Split into Form (Left) and Treeview Table (Right)
        main_paned = ttk.PanedWindow(self, orient="horizontal")
        main_paned.pack(fill="both", expand=True)

        # --- Left Form Frame ---
        form_frame = ttk.LabelFrame(main_paned, text=" Room Details ", padding="15 15 15 15")
        main_paned.add(form_frame, weight=1)

        # Room Number
        ttk.Label(form_frame, text="Room Number:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_room_num = ttk.Entry(form_frame, width=22)
        self.ent_room_num.grid(row=0, column=1, sticky="w", pady=5)

        # Room Type
        ttk.Label(form_frame, text="Room Type:").grid(row=1, column=0, sticky="w", pady=5)
        self.cbo_type = ttk.Combobox(form_frame, values=["Single", "Double", "Deluxe", "Suite"], state="readonly", width=20)
        self.cbo_type.grid(row=1, column=1, sticky="w", pady=5)
        self.cbo_type.current(0)

        # Price Per Night
        ttk.Label(form_frame, text="Price / Night ($):").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_price = ttk.Entry(form_frame, width=22)
        self.ent_price.grid(row=2, column=1, sticky="w", pady=5)

        # Status
        ttk.Label(form_frame, text="Status:").grid(row=3, column=0, sticky="w", pady=5)
        self.cbo_status = ttk.Combobox(form_frame, values=["Available", "Reserved", "Occupied", "Maintenance"], state="readonly", width=20)
        self.cbo_status.grid(row=3, column=1, sticky="w", pady=5)
        self.cbo_status.current(0)

        # Action Buttons
        btn_box = ttk.Frame(form_frame)
        btn_box.grid(row=4, column=0, columnspan=2, pady=(20, 0), sticky="ew")

        btn_add = ttk.Button(btn_box, text="Add Room", command=self.add_room)
        btn_add.pack(side="left", expand=True, fill="x", padx=2)

        btn_update = ttk.Button(btn_box, text="Update", command=self.update_room)
        btn_update.pack(side="left", expand=True, fill="x", padx=2)

        btn_delete = ttk.Button(btn_box, text="Delete", command=self.delete_room)
        btn_delete.pack(side="left", expand=True, fill="x", padx=2)

        btn_clear = ttk.Button(btn_box, text="Clear", command=self.clear_form)
        btn_clear.pack(side="left", expand=True, fill="x", padx=2)

        # --- Right Table Frame ---
        table_frame = ttk.Frame(main_paned)
        main_paned.add(table_frame, weight=3)

        columns = ("room_number", "room_type", "price_per_night", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("room_number", text="Room No.")
        self.tree.heading("room_type", text="Room Type")
        self.tree.heading("price_per_night", text="Price / Night")
        self.tree.heading("status", text="Status")

        self.tree.column("room_number", width=100, anchor="center")
        self.tree.column("room_type", width=120, anchor="center")
        self.tree.column("price_per_night", width=120, anchor="e")
        self.tree.column("status", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def load_rooms(self):
        self.clear_form()
        for item in self.tree.get_children():
            self.tree.delete(item)

        rooms = self.db.get_all_rooms()
        for r in rooms:
            self.tree.insert("", "end", iid=r["room_number"], values=(
                r["room_number"],
                r["room_type"],
                format_currency(r["price_per_night"]),
                r["status"]
            ))

    def search_rooms(self):
        term = self.ent_search.get().strip()
        if not term:
            self.load_rooms()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        rooms = self.db.search_rooms(term)
        for r in rooms:
            self.tree.insert("", "end", iid=r["room_number"], values=(
                r["room_number"],
                r["room_type"],
                format_currency(r["price_per_night"]),
                r["status"]
            ))

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item["values"]

        self.ent_room_num.config(state="normal")
        self.ent_room_num.delete(0, tk.END)
        self.ent_room_num.insert(0, values[0])
        self.ent_room_num.config(state="disabled")  # Primary key disabled on edit

        self.cbo_type.set(values[1])

        clean_price = str(values[2]).replace("$", "").replace(",", "").strip()
        self.ent_price.delete(0, tk.END)
        self.ent_price.insert(0, clean_price)

        self.cbo_status.set(values[3])

    def clear_form(self):
        self.ent_room_num.config(state="normal")
        self.ent_room_num.delete(0, tk.END)
        self.ent_price.delete(0, tk.END)
        self.cbo_type.current(0)
        self.cbo_status.current(0)
        self.ent_search.delete(0, tk.END)

    def add_room(self):
        self.ent_room_num.config(state="normal")
        room_num = self.ent_room_num.get().strip()
        room_type = self.cbo_type.get().strip()
        price_str = self.ent_price.get().strip()
        status = self.cbo_status.get().strip()

        if not room_num:
            messagebox.showwarning("Validation Error", "Please enter a room number.", parent=self)
            return

        if not validate_positive_number(price_str):
            messagebox.showwarning("Validation Error", "Please enter a valid positive room price.", parent=self)
            return

        try:
            self.db.add_room(room_num, room_type, float(price_str), status)
            messagebox.showinfo("Success", f"Room {room_num} added successfully!", parent=self)
            self.load_rooms()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add room: {e}", parent=self)

    def update_room(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Please select a room to update.", parent=self)
            return

        room_num = selected[0]
        room_type = self.cbo_type.get().strip()
        price_str = self.ent_price.get().strip()
        status = self.cbo_status.get().strip()

        if not validate_positive_number(price_str):
            messagebox.showwarning("Validation Error", "Please enter a valid positive room price.", parent=self)
            return

        try:
            self.db.update_room(room_num, room_type, float(price_str), status)
            messagebox.showinfo("Success", f"Room {room_num} updated successfully!", parent=self)
            self.load_rooms()
        except Exception as e:
            messagebox.showerror("Error", f"Could not update room: {e}", parent=self)

    def delete_room(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Please select a room to delete.", parent=self)
            return

        room_num = selected[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Room {room_num}?", parent=self):
            try:
                self.db.delete_room(room_num)
                messagebox.showinfo("Success", f"Room {room_num} deleted successfully!", parent=self)
                self.load_rooms()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete room: {e}", parent=self)
