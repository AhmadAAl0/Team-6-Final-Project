# main_gui.py
import tkinter as tk
from tkinter import messagebox

from classes import (
    Customer, Admin, TicketManager, DataManager,
    SingleRaceTicket, WeekendPass, GroupTicket, Event, Reservation, Discount
)
from gui_functions import clear_screen
from customer_views import show_customer_menu
from admin_views import show_admin_menu

# Initialize managers
tm = TicketManager()
dm = DataManager(folder="gui_data")

# Register ticket types
tm.register_ticket(SingleRaceTicket())
tm.register_ticket(WeekendPass())
tm.register_ticket(GroupTicket(4))
tm.register_ticket(GroupTicket(10))

discounts = [
    Discount("Weekend Promo", 20, "Weekend Pass"),
    Discount("Group Saver", 15, "Group Ticket (4)")
]
dm.save_discounts(discounts)

# Load persisted discounts and sales
for d in dm.load_discounts():
    tm.add_discount(d)
tm._TicketManager__sales_log = dm.load_sales()

# Define some sample events (could be loaded/persisted similarly)
events = [
    Event(date="2025-05-10", location="Yas Marina Circuit"),
    Event(date="2025-05-11", location="Yas Marina Circuit"),
    Event(date="2025-05-12", location="Yas Marina Circuit"),
]

# Load users
users = dm.load_users()
customers = [u for u in users if isinstance(u, Customer)]
admins    = [u for u in users if isinstance(u, Admin)]

# Ensure at least one admin
if not admins:
    default_admin = Admin("Admin", "admin@example.com", "admin123", admin_code="ADMIN001")
    users.append(default_admin)
    admins.append(default_admin)
    dm.save_users(users)

# Set up main window
root = tk.Tk()
root.title("Grand Prix Ticketing System")
root.geometry("500x450")

# -------------------------
# Registration Screen
# -------------------------
def show_registration():
    clear_screen(root)
    tk.Label(root, text="Register New Account", font=("Arial", 16)).pack(pady=10)

    tk.Label(root, text="Name").pack()
    name_entry = tk.Entry(root)
    name_entry.pack()

    tk.Label(root, text="Email").pack()
    email_entry = tk.Entry(root)
    email_entry.pack()

    tk.Label(root, text="Password").pack()
    pass_entry = tk.Entry(root, show="*")
    pass_entry.pack()

    def register_action():
        name = name_entry.get().strip()
        email = email_entry.get().strip()
        pwd  = pass_entry.get()

        if not name or not email or not pwd:
            messagebox.showerror("Error", "All fields are required.")
            return

        # Prevent duplicate emails
        if any(u.get_email()==email for u in customers+admins):
            messagebox.showerror("Error", "Email already registered.")
            return

        try:
            new_cust = Customer(name, email, pwd)
            customers.append(new_cust)
            users.append(new_cust)
            dm.save_users(users)
            messagebox.showinfo("Success", "Registration complete—please log in.")
            show_login()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register: {e}")

    tk.Button(root, text="Register", command=register_action).pack(pady=10)
    tk.Button(root, text="Back to Login", command=show_login).pack(pady=5)

# -------------------------
# Login Screen
# -------------------------
def show_login():
    clear_screen(root)
    tk.Label(root, text="Login", font=("Arial", 16)).pack(pady=10)

    tk.Label(root, text="Email").pack()
    email_entry = tk.Entry(root)
    email_entry.pack()

    tk.Label(root, text="Password").pack()
    pass_entry = tk.Entry(root, show="*")
    pass_entry.pack()

    def login_action():
        email = email_entry.get().strip()
        pwd   = pass_entry.get()
        try:
            for user in customers + admins:
                if user.get_email()==email and user.check_password(pwd):
                    messagebox.showinfo("Welcome", f"Hello, {user.get_name()}")
                    if isinstance(user, Customer):
                        # Pass the events list for reservation screen
                        show_customer_menu(user, root, tm, dm, events)
                    else:
                        show_admin_menu(user, root, tm, dm)
                    return
            raise ValueError("Invalid credentials")
        except Exception as e:
            messagebox.showerror("Login Failed", str(e))

    tk.Button(root, text="Login",    command=login_action).pack(pady=5)
    tk.Button(root, text="Register", command=show_registration).pack(pady=2)

# Launch the app
show_login()
root.mainloop()
