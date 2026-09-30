import tkinter as tk
from tkinter import ttk, messagebox

class LoginFrame(ttk.Frame):
    def __init__(self, parent, db, on_login_success):
        super().__init__(parent)
        self.db = db
        self.on_login_success = on_login_success

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self):
        style = ttk.Style()
        style.configure("LoginHeader.TLabel", font=("Helvetica", 20, "bold"), foreground="#2C3E50")
        style.configure("LoginSub.TLabel", font=("Helvetica", 10), foreground="#7F8C8D")
        style.configure("LoginLabel.TLabel", font=("Helvetica", 11, "bold"))
        style.configure("LoginBtn.TButton", font=("Helvetica", 11, "bold"), padding=6)

    def _build_ui(self):
        # Outer container frame for centering
        center_frame = ttk.Frame(self, padding="40 40 40 40")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Card container
        card = ttk.LabelFrame(center_frame, text=" Hotel Staff Login ", padding="30 20 30 30")
        card.pack(fill="both", expand=True)

        title = ttk.Label(card, text="Hotel Management System", style="LoginHeader.TLabel")
        title.pack(pady=(0, 5))

        subtitle = ttk.Label(card, text="Please authenticate to access the dashboard", style="LoginSub.TLabel")
        subtitle.pack(pady=(0, 25))

        # Username
        lbl_user = ttk.Label(card, text="Username:", style="LoginLabel.TLabel")
        lbl_user.pack(anchor="w", pady=(5, 2))
        self.ent_username = ttk.Entry(card, font=("Helvetica", 11), width=30)
        self.ent_username.pack(fill="x", pady=(0, 15))
        self.ent_username.focus()

        # Password
        lbl_pass = ttk.Label(card, text="Password:", style="LoginLabel.TLabel")
        lbl_pass.pack(anchor="w", pady=(5, 2))
        self.ent_password = ttk.Entry(card, font=("Helvetica", 11), width=30, show="•")
        self.ent_password.pack(fill="x", pady=(0, 20))

        self.ent_password.bind("<Return>", lambda e: self._handle_login())
        self.ent_username.bind("<Return>", lambda e: self.ent_password.focus())

        # Buttons frame
        btn_frame = ttk.Frame(card)
        btn_frame.pack(fill="x", pady=(10, 0))

        btn_login = ttk.Button(btn_frame, text="Login", style="LoginBtn.TButton", command=self._handle_login)
        btn_login.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_clear = ttk.Button(btn_frame, text="Clear", style="LoginBtn.TButton", command=self._handle_clear)
        btn_clear.pack(side="left", expand=True, fill="x", padx=5)

        btn_exit = ttk.Button(btn_frame, text="Exit", style="LoginBtn.TButton", command=self.quit)
        btn_exit.pack(side="left", expand=True, fill="x", padx=(5, 0))

        # Helper hint for demo credentials
        hint_label = ttk.Label(card, text="Default Demo Credentials:\nUsername: admin  |  Password: admin123", style="LoginSub.TLabel", justify="center")
        hint_label.pack(pady=(25, 0))

    def _handle_login(self):
        username = self.ent_username.get().strip()
        password = self.ent_password.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.", parent=self)
            return

        user = self.db.authenticate_user(username, password)
        if user:
            messagebox.showinfo("Success", f"Welcome back, {user['full_name']}!", parent=self)
            self._handle_clear()
            self.on_login_success(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.", parent=self)

    def _handle_clear(self):
        self.ent_username.delete(0, tk.END)
        self.ent_password.delete(0, tk.END)
        self.ent_username.focus()
