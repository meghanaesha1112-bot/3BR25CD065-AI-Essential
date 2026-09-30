import tkinter as tk
from tkinter import ttk, messagebox

class DashboardFrame(ttk.Frame):
    def __init__(self, parent, db, nav_callback):
        super().__init__(parent)
        self.db = db
        self.nav_callback = nav_callback

        self._configure_styles()
        self._build_ui()
        self.refresh_metrics()

    def _configure_styles(self):
        style = ttk.Style()
        style.configure("DashTitle.TLabel", font=("Helvetica", 18, "bold"), foreground="#2C3E50")
        style.configure("CardTitle.TLabel", font=("Helvetica", 10, "bold"), foreground="#7F8C8D")
        style.configure("CardValue.TLabel", font=("Helvetica", 22, "bold"), foreground="#2980B9")
        style.configure("NavBtn.TButton", font=("Helvetica", 11, "bold"), padding=10)

    def _build_ui(self):
        # Header banner
        header = ttk.Frame(self, padding="20 15 20 15")
        header.pack(fill="x")

        lbl_title = ttk.Label(header, text="Dashboard Overview", style="DashTitle.TLabel")
        lbl_title.pack(side="left")

        btn_refresh = ttk.Button(header, text="🔄 Refresh Data", command=self.refresh_metrics)
        btn_refresh.pack(side="right")

        # Metrics cards frame
        cards_frame = ttk.Frame(self, padding="20 10 20 20")
        cards_frame.pack(fill="x")

        # Grid configuration for cards (4 columns)
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)

        self.cards = {}
        metric_configs = [
            ("total_rooms", "Total Rooms", 0, 0, "#3498DB"),
            ("available_rooms", "Available Rooms", 0, 1, "#2ECC71"),
            ("occupied_rooms", "Occupied Rooms", 0, 2, "#E74C3C"),
            ("reserved_rooms", "Reserved Rooms", 0, 3, "#F39C12"),
            ("total_guests", "Total Guests", 1, 0, "#9B59B6"),
            ("today_checkins", "Today Check-ins", 1, 1, "#1ABC9C"),
            ("today_checkouts", "Today Check-outs", 1, 2, "#34495E"),
        ]

        for key, title, row, col, color in metric_configs:
            card = ttk.LabelFrame(cards_frame, text=title, padding="15 10 15 10")
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            val_lbl = ttk.Label(card, text="0", style="CardValue.TLabel")
            val_lbl.pack(pady=5)
            self.cards[key] = val_lbl

        # Quick Navigation Actions section
        nav_section = ttk.LabelFrame(self, text=" Quick Actions ", padding="20 20 20 20")
        nav_section.pack(fill="both", expand=True, padx=20, pady=10)

        nav_buttons = [
            ("🏨 Room Management", "rooms"),
            ("👥 Guest Management", "guests"),
            ("📅 Reservations", "reservations"),
            ("🔑 Check-In", "checkin"),
            ("🚪 Check-Out", "checkout"),
            ("🛎️ Services / Charges", "services"),
            ("💳 Billing & Payments", "billing"),
            ("📊 Reports & Analytics", "reports")
        ]

        # 4 columns for quick action buttons
        for i in range(4):
            nav_section.columnconfigure(i, weight=1)

        for idx, (label, module_key) in enumerate(nav_buttons):
            r = idx // 4
            c = idx % 4
            btn = ttk.Button(
                nav_section,
                text=label,
                style="NavBtn.TButton",
                command=lambda m=module_key: self.nav_callback(m)
            )
            btn.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

    def refresh_metrics(self):
        try:
            metrics = self.db.get_dashboard_metrics()
            for key, val_lbl in self.cards.items():
                val_lbl.config(text=str(metrics.get(key, 0)))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh metrics: {e}", parent=self)
