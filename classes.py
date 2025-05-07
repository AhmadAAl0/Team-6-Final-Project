# classes.py

import uuid
import pickle
import os
from datetime import datetime

# ----------------------------
# Domain Classes
# ----------------------------

class User:
    def __init__(self, name: str, email: str, password: str):
        self.__user_id = str(uuid.uuid4())
        self.__name = name
        self.__email = email
        self.__password = password
        self.__created_at = datetime.now()

    # Getters
    def get_id(self) -> str:
        return self.__user_id

    def get_name(self) -> str:
        return self.__name

    def get_email(self) -> str:
        return self.__email

    def get_created_at(self) -> datetime:
        return self.__created_at

    # Setters
    def set_name(self, name: str):
        self.__name = name

    def set_email(self, email: str):
        self.__email = email

    def set_password(self, password: str):
        self.__password = password

    # Other
    def check_password(self, pw: str) -> bool:
        return self.__password == pw


class Customer(User):
    def __init__(self, name: str, email: str, password: str):
        super().__init__(name, email, password)
        self.__reservations = []

    def get_reservations(self) -> list:
        return list(self.__reservations)

    def add_reservation(self, res):
        self.__reservations.append(res)

    def delete_reservation(self, res_id: str):
        self.__reservations = [
            r for r in self.__reservations if r.get_reservation_id() != res_id
        ]


class Admin(User):
    def __init__(self, name: str, email: str, password: str, admin_code: str):
        super().__init__(name, email, password)
        self.__admin_code = admin_code

    def get_admin_code(self) -> str:
        return self.__admin_code

    def set_admin_code(self, code: str):
        self.__admin_code = code


class Ticket:
    def __init__(self, name: str, price: float, valid_days: int, features: list):
        self.__ticket_id = str(uuid.uuid4())
        self.__name = name
        self.__price = price
        self.__valid_days = valid_days
        self.__features = features

    def get_ticket_id(self) -> str:
        return self.__ticket_id

    def get_name(self) -> str:
        return self.__name

    def set_name(self, name: str):
        self.__name = name

    def get_price(self) -> float:
        return self.__price

    def set_price(self, price: float):
        self.__price = price

    def get_valid_days(self) -> int:
        return self.__valid_days

    def set_valid_days(self, days: int):
        self.__valid_days = days

    def get_features(self) -> list:
        return list(self.__features)

    def set_features(self, features: list):
        self.__features = features


class SingleRaceTicket(Ticket):
    def __init__(self):
        super().__init__(
            name="Single Race Ticket",
            price=300.0,
            valid_days=1,
            features=["Access to one race", "Standard seating"]
        )


class WeekendPass(Ticket):
    def __init__(self):
        super().__init__(
            name="Weekend Pass",
            price=750.0,
            valid_days=3,
            features=["All weekend races", "Premium seating"]
        )


class GroupTicket(Ticket):
    def __init__(self, group_size: int):
        unit_price = max(250.0, 300.0 - group_size * 5)
        total_price = unit_price * group_size
        super().__init__(
            name=f"Group Ticket ({group_size})",
            price=total_price,
            valid_days=1,
            features=["Group seating", "Discounted rate"]
        )
        self.__group_size = group_size

    def get_group_size(self) -> int:
        return self.__group_size

    def set_group_size(self, size: int):
        self.__group_size = size


class Event:
    def __init__(self, date: str, location: str):
        self.__event_id = str(uuid.uuid4())
        self.__date = date
        self.__location = location

    def get_event_id(self) -> str:
        return self.__event_id

    def get_date(self) -> str:
        return self.__date

    def set_date(self, date: str):
        self.__date = date

    def get_location(self) -> str:
        return self.__location

    def set_location(self, location: str):
        self.__location = location


class Reservation:
    def __init__(self, customer_id: str, tickets: list, event: Event, payment_method: str):
        self.__reservation_id = str(uuid.uuid4())
        self.__customer_id = customer_id
        self.__tickets = tickets
        self.__event = event
        self.__total_cost = sum(t.get_price() for t in tickets)
        self.__payment_method = payment_method
        self.__reservation_time = datetime.now()

    def get_reservation_id(self) -> str:
        return self.__reservation_id

    def get_customer_id(self) -> str:
        return self.__customer_id

    def get_tickets(self) -> list:
        return list(self.__tickets)

    def set_tickets(self, tickets: list):
        self.__tickets = tickets
        self.__total_cost = sum(t.get_price() for t in tickets)

    def get_event(self) -> Event:
        return self.__event

    def set_event(self, event: Event):
        self.__event = event

    def get_total_cost(self) -> float:
        return self.__total_cost

    def get_payment_method(self) -> str:
        return self.__payment_method

    def set_payment_method(self, method: str):
        self.__payment_method = method

    def get_reservation_time(self) -> datetime:
        return self.__reservation_time


class Discount:
    def __init__(self, name: str, percentage: int, ticket_type: str):
        self.__name = name
        self.__percentage = percentage
        self.__ticket_type = ticket_type
        self.__active = True

    def get_name(self) -> str:
        return self.__name

    def set_name(self, name: str):
        self.__name = name

    def get_percentage(self) -> int:
        return self.__percentage

    def set_percentage(self, pct: int):
        self.__percentage = pct

    def get_ticket_type(self) -> str:
        return self.__ticket_type

    def set_ticket_type(self, ttype: str):
        self.__ticket_type = ttype

    def is_active(self) -> bool:
        return self.__active

    def activate(self):
        self.__active = True

    def deactivate(self):
        self.__active = False

    def apply_discount(self, price: float) -> float:
        if self.__active:
            return round(price * (1 - self.__percentage / 100), 2)
        return price


# ----------------------------
# Management Classes
# ----------------------------

class TicketManager:
    def __init__(self):
        self.__ticket_types = []
        self.__discounts = []
        self.__sales_log = {}  # date_str -> int

    def register_ticket(self, ticket: Ticket):
        self.__ticket_types.append(ticket)

    def get_ticket_by_name(self, name: str):
        for t in self.__ticket_types:
            if t.get_name() == name:
                return t
        return None

    def get_ticket_types(self) -> list:
        return [t.get_name() for t in self.__ticket_types]

    def add_discount(self, discount: Discount):
        self.__discounts.append(discount)

    def get_active_discounts(self) -> list:
        return [d for d in self.__discounts if d.is_active()]

    def apply_discount(self, ticket: Ticket) -> float:
        for d in self.__discounts:
            if d.get_ticket_type() == ticket.get_name() and d.is_active():
                return d.apply_discount(ticket.get_price())
        return ticket.get_price()

    def record_sale(self, quantity: int = 1):
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.__sales_log[date_str] = self.__sales_log.get(date_str, 0) + quantity

    def get_sales_report(self) -> dict:
        return dict(self.__sales_log)


class DataManager:
    def __init__(self, folder: str = "."):
        self.__folder = folder
        self.__files = {
            "users": os.path.join(folder, "users.pkl"),
            "reservations": os.path.join(folder, "reservations.pkl"),
            "discounts": os.path.join(folder, "discounts.pkl"),
            "sales": os.path.join(folder, "sales.pkl")
        }

    def __load_data(self, key: str):
        path = self.__files[key]
        if not os.path.exists(path):
            return []
        with open(path, "rb") as f:
            return pickle.load(f)

    def __save_data(self, key: str, data):
        path = self.__files[key]
        with open(path, "wb") as f:
            pickle.dump(data, f)

    def save_users(self, users: list):
        self.__save_data("users", users)

    def load_users(self) -> list:
        return self.__load_data("users")

    def save_reservations(self, reservations: list):
        self.__save_data("reservations", reservations)

    def load_reservations(self) -> list:
        return self.__load_data("reservations")

    def save_discounts(self, discounts: list):
        self.__save_data("discounts", discounts)

    def load_discounts(self) -> list:
        return self.__load_data("discounts")

    def save_sales(self, sales: dict):
        self.__save_data("sales", sales)

    def load_sales(self) -> dict:
        data = self.__load_data("sales")
        return data if isinstance(data, dict) else {}

