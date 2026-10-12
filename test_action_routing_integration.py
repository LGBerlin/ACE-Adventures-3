"""Phase 1 integration contracts for the free-text rules engine."""
import random
import unittest
import game
import interaction

class ActionRoutingIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.c=game.new_campaign("Router",1)
        game.add_hero(self.c,game.character("Aster",22,"Fighter",random.Random(4)))
        game.start(self.c)
    def test_mundane_commands_never_roll(self):
        for phrase in ("I look around","check my inventory","view the map","listen","rest"):
            response=interaction.perform(self.c,phrase)
            self.assertFalse(response["roll_required"],phrase)
        self.assertEqual(self.c.get("dice_history",[]),[])
    def test_shop_purchase_from_text_no_roll(self):
        self.c["location"]="market"
        hero=self.c["characters"][0]
        hero["gold"]=25
        out=interaction.perform(self.c,"buy a Healing Draught")
        self.assertFalse(out["roll_required"])
        self.assertEqual(hero["gold"],16)
        self.assertIn("Healing Draught",hero["inventory"])
        out=interaction.perform(self.c,"sell Healing Draught")
        self.assertFalse(out["roll_required"])
        self.assertEqual(hero["gold"],20)
        self.assertNotIn("Healing Draught",hero["inventory"])
    def test_shop_exploits_prevented(self):
        hero=self.c["characters"][0]
        before=hero["gold"]
        with self.assertRaises(ValueError):
            interaction.perform(self.c,"buy a Health Potion")
        self.assertEqual(hero["gold"],before)
        with self.assertRaises(ValueError):
            interaction.perform(self.c,"sell Ashwood Staff")
        self.assertEqual(hero["gold"],before)
    def test_enemy_blocks_shopping_and_travel(self):
        self.c["location"]="market"
        self.c["enemy"]={"name":"Wolf","hp":15,"max_hp":15,"ac":12}
        hero=self.c["characters"][0]
        hero["gold"]=30
        # An action while threatened goes through combat resolution rather than
        # silently granting items or relocating the adventurer.
        with self.assertRaises(ValueError):
            interaction.perform(self.c,"buy a Health Potion",random.Random(1))
        self.assertEqual(hero["gold"],30)
        self.assertNotIn("Health Potion",hero["inventory"])
        self.assertEqual(self.c["location"],"market")
    def test_remote_npc_conversation_does_not_roll(self):
        with self.assertRaises(ValueError):
            interaction.perform(self.c,"I want to ask Mira about the bell")
        self.assertEqual(self.c.get("dice_history",[]),[])
if __name__=="__main__":
    unittest.main()
