import os
import shutil
import uuid
import pickle
import unittest
from datetime import datetime, timedelta

from classes import (
    User, Customer, Admin,
    Ticket, SingleRaceTicket, WeekendPass, GroupTicket,
    Event, Reservation, Discount,
    TicketManager, DataManager
)

class TestUserAndCustomer(unittest.TestCase):
    def setUp(self):
        self.user = User("Alice", "alice@example.com", "pass123")
        self.cust = Customer("Bob", "bob@example.com", "secret")

    def test_user_getters_setters_and_password(self):
        # ID is a UUID
        uuid.UUID(self.user.get_id())
        self.assertEqual(self.user.get_name(), "Alice")
        self.user.set_name("Alicia")
        self.assertEqual(self.user.get_name(), "Alicia")

        self.assertEqual(self.user.get_email(), "alice@example.com")
        self.user.set_email("ali@example.com")
        self.assertEqual(self.user.get_email(), "ali@example.com")

        # password check and setter
        self.assertTrue(self.user.check_password("pass123"))
        self.user.set_password("newpass")
        self.assertTrue(self.user.check_password("newpass"))

        # created_at is recent
        now = datetime.now()
        self.assertTrue(now - self.user.get_created_at() < timedelta(seconds=1))

    def test_customer_reservations(self):
        # initially empty
        self.assertEqual(self.cust.get_reservations(), [])
        # create a dummy reservation
        dummy_event = Event("2025-12-01", "Dubai")
        dummy_ticket = SingleRaceTicket()
        res = Reservation(self.cust.get_id(), [dummy_ticket], dummy_event, "card")
        self.cust.add_reservation(res)
        self.assertEqual(len(self.cust.get_reservations()), 1)
        # delete it
        self.cust.delete_reservation(res.get_reservation_id())
        self.assertEqual(self.cust.get_reservations(), [])

class TestAdmin(unittest.TestCase):
    def setUp(self):
        self.admin = Admin("Manager", "mgr@example.com", "adm1n", "CODEX")

    def test_admin_code_and_inheritance(self):
        self.assertEqual(self.admin.get_admin_code(), "CODEX")
        self.admin.set_admin_code("NEWCODE")
        self.assertEqual(self.admin.get_admin_code(), "NEWCODE")
        # also inherits user methods
        self.assertTrue(self.admin.check_password("adm1n"))
        self.admin.set_password("xyz")
        self.assertTrue(self.admin.check_password("xyz"))

class TestTicketTypes(unittest.TestCase):
    def test_generic_ticket(self):
        t = Ticket("Test", 100.0, 2, ["A", "B"])
        tid = uuid.UUID(t.get_ticket_id())  # id format
        self.assertEqual(t.get_name(), "Test")
        t.set_name("Demo")
        self.assertEqual(t.get_name(), "Demo")

        self.assertEqual(t.get_price(), 100.0)
        t.set_price(120.0)
        self.assertEqual(t.get_price(), 120.0)

        self.assertEqual(t.get_valid_days(), 2)
        t.set_valid_days(5)
        self.assertEqual(t.get_valid_days(), 5)

        self.assertListEqual(t.get_features(), ["A","B"])
        t.set_features(["X"])
        self.assertListEqual(t.get_features(), ["X"])

    def test_specialized_tickets(self):
        s = SingleRaceTicket()
        self.assertEqual(s.get_name(), "Single Race Ticket")
        self.assertEqual(s.get_price(), 300.0)
        self.assertEqual(s.get_valid_days(), 1)
        self.assertIn("Access to one race", s.get_features())

        w = WeekendPass()
        self.assertEqual(w.get_name(), "Weekend Pass")
        self.assertEqual(w.get_price(), 750.0)
        self.assertEqual(w.get_valid_days(), 3)

        g = GroupTicket(4)
        # unit_price = max(250, 300 - 4*5) = 280, total = 280*4
        self.assertEqual(g.get_price(), 280 * 4)
        self.assertEqual(g.get_group_size(), 4)
        g.set_group_size(5)
        self.assertEqual(g.get_group_size(), 5)

class TestEventAndReservation(unittest.TestCase):
    def setUp(self):
        self.event = Event("2025-11-05", "Abu Dhabi")
        self.t1 = SingleRaceTicket()
        self.t2 = WeekendPass()

    def test_event_fields(self):
        eid = uuid.UUID(self.event.get_event_id())
        self.assertEqual(self.event.get_date(), "2025-11-05")
        self.event.set_date("2025-12-01")
        self.assertEqual(self.event.get_date(), "2025-12-01")
        self.assertEqual(self.event.get_location(), "Abu Dhabi")
        self.event.set_location("Dubai")
        self.assertEqual(self.event.get_location(), "Dubai")

    def test_reservation_logic(self):
        res = Reservation("cust123", [self.t1, self.t2], self.event, "wallet")
        rid = uuid.UUID(res.get_reservation_id())
        self.assertEqual(res.get_customer_id(), "cust123")
        self.assertListEqual([t.get_ticket_id() for t in res.get_tickets()],
                             [self.t1.get_ticket_id(), self.t2.get_ticket_id()])
        # total cost = 300 + 750
        self.assertEqual(res.get_total_cost(), 1050.0)
        # change tickets
        new_tix = [self.t1]
        res.set_tickets(new_tix)
        self.assertEqual(res.get_total_cost(), 300.0)
        # payment method
        self.assertEqual(res.get_payment_method(), "wallet")
        res.set_payment_method("card")
        self.assertEqual(res.get_payment_method(), "card")
        # reservation_time is recent
        self.assertTrue(datetime.now() - res.get_reservation_time() < timedelta(seconds=1))

class TestDiscount(unittest.TestCase):
    def setUp(self):
        self.disc = Discount("EarlyBird", 20, "Single Race Ticket")

    def test_discount_fields_and_apply(self):
        self.assertEqual(self.disc.get_name(), "EarlyBird")
        self.disc.set_name("LateBird")
        self.assertEqual(self.disc.get_name(), "LateBird")

        self.assertEqual(self.disc.get_percentage(), 20)
        self.disc.set_percentage(50)
        self.assertEqual(self.disc.get_percentage(), 50)

        self.assertEqual(self.disc.get_ticket_type(), "Single Race Ticket")
        self.disc.set_ticket_type("Weekend Pass")
        self.assertEqual(self.disc.get_ticket_type(), "Weekend Pass")

        self.assertTrue(self.disc.is_active())
        price = 100.0
        # 50% off
        self.assertEqual(self.disc.apply_discount(price), 50.0)
        self.disc.deactivate()
        self.assertFalse(self.disc.is_active())
        self.assertEqual(self.disc.apply_discount(price), 100.0)

class TestTicketManager(unittest.TestCase):
    def setUp(self):
        self.tm = TicketManager()
        # register sample tickets
        self.t1 = SingleRaceTicket()
        self.t2 = WeekendPass()
        self.tm.register_ticket(self.t1)
        self.tm.register_ticket(self.t2)
        # add a discount
        self.disc = Discount("GroupSale", 10, self.t2.get_name())
        self.tm.add_discount(self.disc)

    def test_ticket_lookup_and_types(self):
        self.assertEqual(self.tm.get_ticket_by_name(self.t1.get_name()), self.t1)
        self.assertListEqual(sorted(self.tm.get_ticket_types()),
                             sorted([self.t1.get_name(), self.t2.get_name()]))

    def test_discounts_and_sales(self):
        # discount applies only to WeekendPass
        price = self.tm.apply_discount(self.t2)
        self.assertEqual(price, round(750 * 0.9, 2))
        # no discount for SingleRaceTicket
        self.assertEqual(self.tm.apply_discount(self.t1), 300.0)

        # record sales
        self.tm.record_sale(2)
        rpt = self.tm.get_sales_report()
        today = datetime.now().strftime("%Y-%m-%d")
        self.assertEqual(rpt.get(today), 2)
        # record more
        self.tm.record_sale(3)
        rpt2 = self.tm.get_sales_report()
        self.assertEqual(rpt2.get(today), 5)

class TestDataManager(unittest.TestCase):
    TEST_DIR = "test_data_mgr"

    def setUp(self):
        # create fresh folder
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)
        os.mkdir(self.TEST_DIR)
        self.dm = DataManager(folder=self.TEST_DIR)

    def tearDown(self):
        shutil.rmtree(self.TEST_DIR)

    def test_users_persistence(self):
        users = [User("X","x@x.com","pw"), User("Y","y@y.com","pw2")]
        self.dm.save_users(users)
        loaded = self.dm.load_users()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].get_email(), "x@x.com")

    def test_reservations_persistence(self):
        ev = Event("2025-01-01", "TestCity")
        res = Reservation("cid", [SingleRaceTicket()], ev, "card")
        self.dm.save_reservations([res])
        loaded = self.dm.load_reservations()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].get_customer_id(), "cid")

    def test_discounts_persistence(self):
        disc = Discount("D","20","Single Race Ticket")
        self.dm.save_discounts([disc])
        loaded = self.dm.load_discounts()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].get_name(), "D")

    def test_sales_persistence(self):
        sales = {"2025-05-10": 7}
        self.dm.save_sales(sales)
        loaded = self.dm.load_sales()
        self.assertIsInstance(loaded, dict)
        self.assertEqual(loaded.get("2025-05-10"), 7)


if __name__ == "__main__":
    unittest.main()
