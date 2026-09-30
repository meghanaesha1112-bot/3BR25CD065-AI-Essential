import tkinter as tk
from tkinter import ttk, messagebox
import os

from database import Database
from login import LoginFrame
from dashboard import DashboardFrame
from rooms import RoomsFrame
from guests import GuestsFrame
from reservations import ReservationsFrame
from checkin import CheckInFrame
from checkout import CheckOutFrame
from services import ServicesFrame
from billing import BillingFrame
from reports import ReportsFrame

class HotelApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Hotel Management System")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        # Set ttk style theme
        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        # Initialize Database
        self.db = Database()

        # Application state
        self.current_user = None
        self.active_frame = None

        # Main Layout Containers
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.sidebar = None
        self.content_area = None

        # Start with Login Screen
        self.show_login()

    def show_login(self):
        self._clear_container()
        self.current_user = None

        login_frame = LoginFrame(self.container, self.db, self.on_login_success)
        login_frame.pack(fill="both", expand=True)
        self.active_frame = login_frame

    def on_login_success(self, user):
        self.current_user = user
        self._build_main_layout()
        self.navigate_to("dashboard")

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _build_main_layout(self):
        self._clear_container()

        # Top Bar
        top_bar = ttk.Frame(self.container, padding="10 10 15 10")
        top_bar.pack(side="top", fill="x")

        app_title = ttk.Label(top_bar, text="🏨 Grand Hotel Management System", font=("Helvetica", 14, "bold"))
        app_title.pack(side="left")

        user_info = ttk.Label(
            top_bar,
            text=f"User: {self.current_user['full_name']} ({self.current_user['role']})",
            font=("Helvetica", 10, "italic")
        )
        user_info.pack(side="right", padx=(10, 20))

        btn_logout = ttk.Button(top_bar, text="Logout 🚪", command=self.logout)
        btn_logout.pack(side="right")

        # Divider line
        sep = ttk.Separator(self.container, orient="horizontal")
        sep.pack(side="top", fill="x")

        # Main Workspace (Sidebar + Content)
        workspace = ttk.Frame(self.container)
        workspace.pack(side="top", fill="both", expand=True)

        # Navigation Sidebar
        self.sidebar = ttk.Frame(workspace, padding="10 10 10 10", width=200)
        self.sidebar.pack(side="left", fill="y", padx=(0, 2))

        # Vertical Separator between sidebar and content
        v_sep = ttk.Separator(workspace, orient="vertical")
        v_sep.pack(side="left", fill="y")

        # Content Area
        self.content_area = ttk.Frame(workspace, padding="10 10 10 10")
        self.content_area.pack(side="right", fill="both", expand=True)

        # Add Navigation Buttons
        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("🏨 Rooms", "rooms"),
            ("👥 Guests", "guests"),
            ("📅 Reservations", "reservations"),
            ("🔑 Check-In", "checkin"),
            ("🚪 Check-Out", "checkout"),
            ("🛎️ Services", "services"),
            ("💳 Billing", "billing"),
            ("📈 Reports", "reports")
        ]

        lbl_nav = ttk.Label(self.sidebar, text="NAVIGATION", font=("Helvetica", 9, "bold"), foreground="#7F8C8D")
        lbl_nav.pack(anchor="w", pady=(5, 10))

        self.nav_buttons = {}
        for label, module_key in nav_items:
            btn = ttk.Button(
                self.sidebar,
                text=label,
                command=lambda m=module_key: self.navigate_to(m)
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[module_key] = btn

    def navigate_to(self, module_key):
        if not self.content_area:
            return

        # Clear existing view in content_area
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Instantiate module frame
        frame = None
        if module_key == "dashboard":
            frame = DashboardFrame(self.content_area, self.db, self.navigate_to)
        elif module_key == "rooms":
            frame = RoomsFrame(self.content_area, self.db)
        elif module_key == "guests":
            frame = GuestsFrame(self.content_area, self.db)
        elif module_key == "reservations":
            frame = ReservationsFrame(self.content_area, self.db)
        elif module_key == "checkin":
            frame = CheckInFrame(self.content_area, self.db)
        elif module_key == "checkout":
            frame = CheckOutFrame(self.content_area, self.db)
        elif module_key == "services":
            frame = ServicesFrame(self.content_area, self.db)
        elif module_key == "billing":
            frame = BillingFrame(self.content_area, self.db)
        elif module_key == "reports":
            frame = ReportsFrame(self.content_area, self.db)

        if frame:
            frame.pack(fill="both", expand=True)
            self.active_frame = frame

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?", parent=self):
            self.show_login()

if __name__ == "__main__":
    app = HotelApp()
    app.mainloop()
