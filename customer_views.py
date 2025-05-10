# customer_views.py
# Handles customer interactions: view, create, modify reservations

import tkinter as tk
from tkinter import messagebox
from datetime import datetime  # for timestamping sales
from classes import Reservation
from gui_functions import clear_screen

# Display the main customer menu with reservation actions
# tm: TicketManager instance; dm: DataManager instance; events: list of Event

def show_customer_menu(customer, root, tm, dm, events):
    clear_screen(root)
    tk.Label(root, text=f"Welcome, {customer.get_name()}", font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="Edit My Details", command=lambda: edit_customer_details(customer, root, tm, dm, events)).pack(pady=5)
    tk.Button(
        root, text="My Reservations",
        command=lambda: show_reservations(customer, root, tm, dm, events)
    ).pack(pady=5)
    tk.Button(
        root, text="Make Reservation",
        command=lambda: make_reservation(customer, root, tm, dm, events)
    ).pack(pady=5)
    tk.Button(root, text="Logout", command=lambda: root.destroy()).pack(pady=20)

def edit_customer_details(customer, root, tm, dm, events):
    clear_screen(root)
    tk.Label(root, text="Edit Account Details", font=("Arial", 14)).pack(pady=10)

    tk.Label(root, text="Name").pack()
    name_entry = tk.Entry(root)
    name_entry.insert(0, customer.get_name())
    name_entry.pack()

    tk.Label(root, text="Email").pack()
    email_entry = tk.Entry(root)
    email_entry.insert(0, customer.get_email())
    email_entry.pack()

    tk.Label(root, text="Password").pack()
    pw_entry = tk.Entry(root, show="*")
    pw_entry.pack()

    def save_changes():
        try:
            customer.set_name(name_entry.get())
            customer.set_email(email_entry.get())
            if pw_entry.get():  # optional
                customer.set_password(pw_entry.get())

            # Persist changes
            users = dm.load_users()
            for i, u in enumerate(users):
                if u.get_id() == customer.get_id():
                    users[i] = customer
            dm.save_users(users)

            messagebox.showinfo("Success", "Your account details were updated.")
            show_customer_menu(customer, root, tm, dm, events)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(root, text="Save", command=save_changes).pack(pady=10)
    tk.Button(root, text="Back", command=lambda: show_customer_menu(customer, root, tm, dm, events)).pack()


# Show a list of current reservations with summary info

def show_reservations(customer, root, tm, dm, events):
    clear_screen(root)
    tk.Label(root, text="Your Reservations", font=("Arial", 14)).pack(pady=10)
    reservations = customer.get_reservations()
    if not reservations:
        tk.Label(root, text="No reservations found.").pack(pady=10)
    else:
        for res in reservations:
            summary = (
                f"ID: {res.get_reservation_id()} | "
                f"Event: {res.get_event().get_date()} at {res.get_event().get_location()} | "
                f"Tickets: {', '.join(t.get_name() for t in res.get_tickets())} | "
                f"Total: AED {res.get_total_cost()}"
            )
            tk.Label(root, text=summary, anchor="w", justify="left").pack(fill="x", padx=10, pady=2)
    tk.Button(root, text="Back", command=lambda: show_customer_menu(customer, root, tm, dm, events)).pack(pady=20)

# GUI to create a new reservation for a selected event and ticket

def make_reservation(customer, root, tm, dm, events):
    clear_screen(root)
    tk.Label(root, text="Make Reservation", font=("Arial", 14)).pack(pady=10)

    # Event selection by ID - use human-readable later
    tk.Label(root, text="Select Event").pack()
    event_var = tk.StringVar(value=events[0].get_event_id())
    tk.OptionMenu(root, event_var, *[e.get_event_id() for e in events]).pack()

    # Ticket type selection
    tk.Label(root, text="Select Ticket Type").pack()
    types = tm.get_ticket_types()
    ticket_var = tk.StringVar(value=types[0] if types else "")
    tk.OptionMenu(root, ticket_var, *types).pack()

    # Payment method selection
    tk.Label(root, text="Payment Method").pack()
    pay_var = tk.StringVar(value="Credit Card")
    tk.OptionMenu(root, pay_var, "Credit Card", "Debit Card", "Apple Pay", "Google Pay").pack()

    def confirm():
        try:
            # Find the actual Event object
            ev = next((e for e in events if e.get_event_id() == event_var.get()), None)
            if ev is None:
                raise ValueError("Invalid event selected.")

            ticket = tm.get_ticket_by_name(ticket_var.get())
            if ticket is None:
                raise ValueError("Invalid ticket type selected.")

            # Calculate price with discounts
            price = tm.apply_discount(ticket)
            method = pay_var.get()

            # Create reservation object
            reservation = Reservation(
                customer_id=customer.get_id(),
                tickets=[ticket],
                event=ev,
                payment_method=method
            )

            # Update in-memory state
            customer.add_reservation(reservation)
            tm.record_sale(1)

            # Persist customers
            users = dm.load_users()
            updated = False
            for idx, u in enumerate(users):
                if u.get_id() == customer.get_id():
                    users[idx] = customer
                    updated = True
            if not updated:
                users.append(customer)
            dm.save_users(users)

            # Persist reservations list
            all_res = dm.load_reservations()
            if not isinstance(all_res, list):
                all_res = []
            all_res.append(reservation)
            dm.save_reservations(all_res)

            # Persist sales log safely
            sales = dm.load_sales()
            if not isinstance(sales, dict):
                sales = {}
            date_str = datetime.now().strftime("%Y-%m-%d")
            sales[date_str] = sales.get(date_str, 0) + 1
            dm.save_sales(sales)

            messagebox.showinfo("Success", f"Reserved {ticket.get_name()} on {ev.get_date()} for AED {price}")
            show_customer_menu(customer, root, tm, dm, events)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(root, text="Confirm", command=confirm).pack(pady=10)
    tk.Button(root, text="Back", command=lambda: show_customer_menu(customer, root, tm, dm, events)).pack(pady=5)
