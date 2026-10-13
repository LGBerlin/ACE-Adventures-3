import random
import tempfile
import unittest
import dice_ledger
import game
import interaction

class DiceLedgerTests(unittest.TestCase):
    def setUp(self):
        self.c=game.new_campaign("Dice records",1)
        game.add_hero(self.c,game.character("Ada",23,"Fighter",random.Random(7)))
        game.start(self.c)
    def test_nonroll_does_not_create_record(self):
        interaction.perform(self.c,"look around")
        self.assertEqual(dice_ledger.history(self.c),[])
    def test_combat_roll_recorded_and_persisted(self):
        game.encounter(self.c,random.Random(2))
        outcome=interaction.perform(self.c,"I attack the enemy",random.Random(3))
        self.assertTrue(outcome["roll_required"])
        self.assertEqual(len(dice_ledger.history(self.c)),1)
        self.assertEqual(dice_ledger.history(self.c)[0]["roll"],outcome["roll"])
        with tempfile.TemporaryDirectory() as folder:
            game.save(folder,self.c)
            self.assertEqual(game.load_all(folder)[0]["dice_history"],self.c["dice_history"])
    def test_history_is_bounded(self):
        result=dict(roll_required=True,roll=10,modifier=2,total=12,dc=12,degree="Success")
        for n in range(60):dice_ledger.record(self.c,result,"attack "+str(n))
        self.assertEqual(len(dice_ledger.history(self.c)),40)
    def test_malformed_roll_rejected(self):
        self.assertIsNone(dice_ledger.record(self.c,dict(roll_required=True,roll=0,modifier=0,total=0,dc=12),"bad"))
        self.assertEqual(dice_ledger.history(self.c),[])
if __name__=="__main__":unittest.main()
