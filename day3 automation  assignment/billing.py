import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils import format_currency

class BillingFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        self._build_ui()
        self.load_bills()

    def _build_ui(self):
        # Header / Title Frame
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Billing & Invoicing Records", font=("Helvetica", 16, "bold"), foreground="#2C3E50").pack(side="left")

        # Top Search Bar
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Search Bill / Guest:").pack(side="left", padx=(0, 5))
        self.ent_search = ttk.Entry(search_frame, width=25)
        self.ent_search.pack(side="left", padx=(0, 5))
        self.ent_search.bind("<Return>", lambda e: self.search_bills())

        btn_search = ttk.Button(search_frame, text="Search", command=self.search_bills)
        btn_search.pack(side="left", padx=(0, 5))

        btn_refresh = ttk.Button(search_frame, text="Reset / Refresh", command=self.load_bills)
        btn_refresh.pack(side="left")

        main_paned = ttk.PanedWindow(self, orient="horizontal")
        main_paned.pack(fill="both", expand=True)

        # --- Left Table: All Invoices / Bills ---
        table_frame = ttk.LabelFrame(main_paned, text=" Billing History ", padding="10 10 10 10")
        main_paned.add(table_frame, weight=3)

        columns = ("bill_number", "guest_name", "room_number", "grand_total", "created_at")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("bill_number", text="Bill No.")
        self.tree.heading("guest_name", text="Guest Name")
        self.tree.heading("room_number", text="Room No.")
        self.tree.heading("grand_total", text="Grand Total")
        self.tree.heading("created_at", text="Issued Date")

        self.tree.column("bill_number", width=140, anchor="center")
        self.tree.column("guest_name", width=140, anchor="w")
        self.tree.column("room_number", width=70, anchor="center")
        self.tree.column("grand_total", width=100, anchor="e")
        self.tree.column("created_at", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # --- Right Frame: Printable Invoice Preview ---
        preview_frame = ttk.LabelFrame(main_paned, text=" Invoice Detailed Preview ", padding="15 15 15 15")
        main_paned.add(preview_frame, weight=2)

        self.txt_invoice = tk.Text(preview_frame, wrap="word", font=("Courier", 10), state="disabled", width=45)
        self.txt_invoice.pack(fill="both", expand=True, pady=(0, 10))

        btn_export = ttk.Button(preview_frame, text="Export / Print Bill 📄", command=self.export_bill)
        btn_export.pack(fill="x")

        self.selected_bill = None

    def load_bills(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.ent_search.delete(0, tk.END)
        bills = self.db.get_all_bills()
        for b in bills:
            self.tree.insert("", "end", iid=b["bill_number"], values=(
                b["bill_number"],
                b["guest_name"],
                b["room_number"],
                format_currency(b["grand_total"]),
                b["created_at"]
            ))

    def search_bills(self):
        term = self.ent_search.get().strip()
        if not term:
            self.load_bills()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        bills = self.db.search_bills(term)
        for b in bills:
            self.tree.insert("", "end", iid=b["bill_number"], values=(
                b["bill_number"],
                b["guest_name"],
                b["room_number"],
                format_currency(b["grand_total"]),
                b["created_at"]
            ))

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        bill_num = selected[0]
        bills = self.db.get_all_bills()
        matched = [b for b in bills if b["bill_number"] == bill_num]

        if matched:
            b = matched[0]
            self.selected_bill = b
            self._render_invoice_text(b)

    def _render_invoice_text(self, b):
        self.txt_invoice.config(state="normal")
        self.txt_invoice.delete("1.0", tk.END)

        invoice_str = f"""
=============================================
         GRAND HOTEL & RESORT
       123 Luxury Way, Metropolis
          Phone: +1-800-555-0199
=============================================
OFFICIAL RECEIPT / INVOICE

Invoice No : {b['bill_number']}
Date Issued: {b['created_at']}
Guest Name : {b['guest_name']}
Room Number: {b['room_number']}
---------------------------------------------
Check-In   : {b['check_in_date']}
Check-Out  : {b['check_out_date']}
Total Stay : {b['total_nights']} Night(s)
---------------------------------------------
CHARGES BREAKDOWN:
Room Rate / Night  : {format_currency(b['room_price_per_night'])}
Total Room Charges : {format_currency(b['room_charges'])}
Service Charges    : {format_currency(b['service_charges'])}
---------------------------------------------
Subtotal           : {format_currency(b['room_charges'] + b['service_charges'])}
Discount           : -{format_currency(b['discount'])}
Tax ({b['tax_rate']}%)        : {format_currency(b['tax_amount'])}
=============================================
GRAND TOTAL        : {format_currency(b['grand_total'])}
Payment Status     : {b['payment_status']}
=============================================
     Thank you for staying with us!
"""
        self.txt_invoice.insert("1.0", invoice_str)
        self.txt_invoice.config(state="disabled")

    def export_bill(self):
        if not self.selected_bill:
            messagebox.showwarning("Export Error", "Please select an invoice from the list first.", parent=self)
            return

        file_path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=f"{self.selected_bill['bill_number']}.txt"
        )

        if file_path:
            try:
                content = self.txt_invoice.get("1.0", tk.END)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Invoice successfully saved to:\n{file_path}", parent=self)
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not save invoice: {e}", parent=self)
