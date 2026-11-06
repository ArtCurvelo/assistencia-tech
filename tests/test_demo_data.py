import unittest
from assistencia_tech.services.demo_data import initial_clients, initial_equipment, initial_orders

class DemoDataTests(unittest.TestCase):
    def test_seed_data_has_expected_collections(self):
        self.assertGreaterEqual(len(initial_clients()), 3)
        self.assertGreaterEqual(len(initial_equipment()), 3)
        self.assertGreaterEqual(len(initial_orders()), 3)

    def test_order_codes_are_unique(self):
        codes = [order["code"] for order in initial_orders()]
        self.assertEqual(len(codes), len(set(codes)))

    def test_order_statuses_are_known(self):
        allowed = {"Recebido", "Em análise", "Em reparo", "Concluído"}
        self.assertTrue(all(order["status"] in allowed for order in initial_orders()))

if __name__ == "__main__":
    unittest.main()
