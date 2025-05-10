# admin_views.py
# Handles admin interactions: view sales and manage discounts

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from gui_functions import clear_screen

# Display the main admin menu with report and discount actions
# tm: TicketManager instance; dm: DataManager instance

def show_admin_menu(admin, root, tm, dm):
    clear_screen(root)
    tk.Label(root, text=f"Admin: {admin.get_name()}", font=("Arial", 16)).pack(pady=10)
    tk.Button(
        root, text="View Sales Report",
        command=lambda: view_sales_report(root, tm)
    ).pack(pady=5)
    tk.Button(
        root, text="Manage Discounts",
        command=lambda: manage_discounts(admin, root, tm, dm)
    ).pack(pady=5)
    tk.Button(
        root, text="Logout",
        command=lambda: root.destroy()
    ).pack(pady=20)

# Show a detailed sales report in a popup

def view_sales_report(root, tm):
    try:
        sales = tm.get_sales_report()
        if not sales:
            raise ValueError("No sales data available.")
        report = "\n".join([f"{date}: {count} tickets" for date, count in sales.items()])
        messagebox.showinfo("Sales Report", report)
    except ValueError as ve:
        messagebox.showwarning("No Data", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"Unable to load sales report: {e}")

# GUI for managing discount activation and deactivation

def manage_discounts(admin, root, tm, dm):
    clear_screen(root)
    tk.Label(root, text="Manage Discounts", font=("Arial", 14)).pack(pady=10)

    discounts = tm.get_active_discounts() + [d for d in tm._TicketManager__discounts if not d.is_active()]
    for discount in discounts:
        frame = tk.Frame(root)
        frame.pack(fill="x", padx=10, pady=3)

        status = "Active" if discount.is_active() else "Inactive"
        text = f"{discount.get_name()} ({discount.get_percentage()}% off on {discount.get_ticket_type()}) - {status}"
        tk.Label(frame, text=text).pack(side="left", expand=True)

        def toggle(d=discount):
            try:
                if d.is_active():
                    d.deactivate()
                else:
                    d.activate()
                dm.save_discounts(tm._TicketManager__discounts)
                messagebox.showinfo(
                    "Updated",
                    f"{d.get_name()} is now {'Active' if d.is_active() else 'Inactive'}"
                )
                manage_discounts(admin, root, tm, dm)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to toggle discount: {e}")

        tk.Button(frame, text="Toggle", command=toggle).pack(side="right")

    tk.Button(
        root,
        text="Back to Menu",
        command=lambda: show_admin_menu(admin, root, tm, dm)
    ).pack(pady=15)
