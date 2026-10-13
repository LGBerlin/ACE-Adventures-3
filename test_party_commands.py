import random
import tempfile
import unittest
import game
import interaction
class PartyCommandsTests(unittest.TestCase):
    def setUp(self):
        self.c=game.new_campaign("Party switching",2)
        game.add_hero(self.c,game.character("Aster",22,"Fighter",random.Random(1)))
        game.add_hero(self.c,game.character("Bryn",24,"Rogue",random.Random(2)))
        game.start(self.c)
    def test_switch_without_roll_and_save(self):
        response=interaction.perform(self.c,"switch to Bryn")
        self.assertFalse(response["roll_required"])
        self.assertEqual(self.c["active"],1)
        self.assertEqual(self.c.get("dice_history",[]),[])
        with tempfile.TemporaryDirectory() as folder:
            game.save(folder,self.c)
            self.assertEqual(game.load_all(folder)[0]["active"],1)
    def test_switch_in_battle_does_not_consume_turn(self):
        game.encounter(self.c,random.Random(3))
        before=self.c["turn"]
        response=interaction.perform(self.c,"play as Bryn")
        self.assertFalse(response["roll_required"])
        self.assertEqual(self.c["turn"],before)
        self.assertEqual(self.c["active"],1)
    def test_unknown_character_cannot_be_created_by_command(self):
        with self.assertRaises(ValueError):
            interaction.perform(self.c,"select Unknown Wizard")
        self.assertEqual(len(self.c["characters"]),2)
if __name__=="__main__":unittest.main()
