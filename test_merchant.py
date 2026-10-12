"""Contract tests for the rules-authoritative merchant UI backend."""
import random
import tempfile
import unittest
import game
import merchant

class MerchantTests(unittest.TestCase):
    def setUp(self):
        self.c = game.new_campaign("Merchant tests", 1)
        game.add_hero(self.c, game.character("Aster", 24, "Fighter", random.Random(4)))
        game.start(self.c)
        self.h = self.c["characters"][0]
    def test_buy_sell_roundtrip_and_save(self):
        self.c["location"] = "market"
        self.h["gold"] = 40
        merchant.buy(self.c, "Healing Draught")
        self.assertEqual(self.h["gold"], 31)
        self.assertIn("Healing Draught", self.h["inventory"])
        merchant.sell(self.c, "Healing Draught")
        self.assertEqual(self.h["gold"], 35)
        self.assertNotIn("Healing Draught", self.h["inventory"])
        with tempfile.TemporaryDirectory() as folder:
            game.save(folder, self.c)
            loaded = game.load_all(folder)[0]
            self.assertEqual(loaded["characters"][0]["gold"], 35)
    def test_no_free_items_or_gold(self):
        self.c["location"] = "market"
        self.h["gold"] = 0
        with self.assertRaises(ValueError):
            merchant.buy(self.c, "Iron Sword")
        with self.assertRaises(ValueError):
            merchant.sell(self.c, "Iron Sword")
        self.assertEqual(self.h["gold"], 0)
    def test_requires_market_and_no_enemy(self):
        with self.assertRaises(ValueError):
            merchant.buy(self.c, "Travel Rations")
        self.c["location"] = "market"
        self.c["enemy"] = {"name": "Wolf", "hp": 10, "ac": 12}
        with self.assertRaises(ValueError):
            merchant.buy(self.c, "Travel Rations")
    def test_invalid_stock_is_rejected(self):
        self.c["location"] = "market"
        with self.assertRaises(ValueError):
            merchant.buy(self.c, "Free Legendary Sword")
if __name__ == "__main__":
    unittest.main()
