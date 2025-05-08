"""
testing.py

This script exercises all core functionality of the classes defined in classes.py.
Each section is commented to explain what is being tested.
"""

import os
import uuid
from classes import (
    User, Customer, Admin,
    Ticket, SingleRaceTicket, WeekendPass, GroupTicket,
    Event, Reservation, Discount,
    TicketManager, DataManager
)

# Ensure a clean test environment by removing existing pickle files
dm = DataManager(folder="test_data")
for key, path in dm._DataManager__files.items():
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

# ----------------------------
# 1. User Creation and Accessors
# ----------------------------
# Create a customer and admin, test getters and setters
cust = Customer("Ahmad", "ahmad@example.com", "Ahmadpass")
admin = Admin("Yousif", "yousif@example.com", "Yousifpass", admin_code="ADM001")

# Test User getters
print("User ID:", cust.get_id())
print("Name:", cust.get_name())
print("Email:", cust.get_email())

# Test setters
cust.set_name("Ahmed Mahmood")
cust.set_email("Ahmed.Mahmood@example.com")
cust.set_password("newpass")
print("Updated Name:", cust.get_name())
print("Updated Email:", cust.get_email())
print("Password Valid:", cust.check_password("newpass"))

# ----------------------------
# 2. Ticket Types and Discounts
# ----------------------------
# Instantiate different ticket types
single = SingleRaceTicket()
weekend = WeekendPass()
group = GroupTicket(group_size=4)

# Verify base prices
print("Single Ticket Price:", single.get_price())
print("Weekend Pass Price:", weekend.get_price())
print("Group Ticket Price:", group.get_price(), "(for 4 people)")

# Create and test a discount
disc = Discount(name="Weekend Promo", percentage=20, ticket_type="Weekend Pass")
print("Discount active?", disc.is_active())
discounted_price = disc.apply_discount(weekend.get_price())
print("Discounted Weekend Pass Price:", discounted_price)

# Deactivate and test that price returns to full
disc.deactivate()
print("Discount active after deactivate?", disc.is_active())
print("Price after deactivation:", disc.apply_discount(weekend.get_price()))

# ----------------------------
# 3. TicketManager Functionality
# ----------------------------
tm = TicketManager()
# Register tickets and discounts
tm.register_ticket(single)
tm.register_ticket(weekend)
tm.register_ticket(group)
tm.add_discount(disc)

# List available ticket names
print("Registered Ticket Types:", tm.get_ticket_types())

# Test discount application via manager
print("Manager applies discount (should be full price):", tm.apply_discount(weekend))

# Reactivate discount and test
disc.activate()
print("Manager applies discount (20% off):", tm.apply_discount(weekend))

# Record and report sales
tm.record_sale(quantity=3)
tm.record_sale(quantity=2)
print("Sales Log:", tm.get_sales_report())

# ----------------------------
# 4. Reservation Workflow
# ----------------------------
# Create an event
event = Event(date="2025-05-10", location="Yas Marina Circuit")
print("Event Info:", event.get_date(), event.get_location())

# Make a reservation for the customer
reservation = Reservation(
    customer_id=cust.get_id(),
    tickets=[single, group],
    event=event,
    payment_method="Credit Card"
)

# Confirm reservation details
print("Reservation ID:", reservation.get_reservation_id())
print("Reservation Total Cost:", reservation.get_total_cost())

# Modify payment method and ticket list
reservation.set_payment_method("Debit Card")
print("Updated Payment Method:", reservation.get_payment_method())
reservation.set_tickets([single])  # remove group ticket
print("Updated Total Cost:", reservation.get_total_cost())

# ----------------------------
# 5. Customer Reservation Management
# ----------------------------
cust.add_reservation(reservation)
print("Customer Reservations after add:", cust.get_reservations())

# Delete reservation
cust.delete_reservation(reservation.get_reservation_id())
print("Customer Reservations after delete:", cust.get_reservations())

# ----------------------------
# 6. Persistence with DataManager
# ----------------------------
# Save users, reservations, discounts, and sales to disk
dm.save_users([cust, admin])
dm.save_reservations([reservation])
dm.save_discounts([disc])
dm.save_sales(tm.get_sales_report())

# Load back from disk and verify
loaded_users = dm.load_users()
loaded_reservations = dm.load_reservations()
loaded_discounts = dm.load_discounts()
loaded_sales = dm.load_sales()

print("Loaded Users:", [u.get_email() for u in loaded_users])
print("Loaded Reservations:", [r.get_reservation_id() for r in loaded_reservations])
print("Loaded Discounts:", [d.get_name() for d in loaded_discounts])
print("Loaded Sales:", loaded_sales)