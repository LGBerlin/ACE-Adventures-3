"""Boss-phase gameplay acceptance tests."""
import random
import unittest
import game

class GuardianPhases(unittest.TestCase):
    def setUp(self):
        self.c=game.new_campaign("Guardian phases",1)
        game.add_hero(self.c,game.character("Aster",24,"Fighter",random.Random(4)))
        game.start(self.c)
        self.c["quest"]={"stage":3,"completed":False}
        game.encounter(self.c,random.Random(2))
    def test_guardian_changes_attack_when_below_half_health(self):
        class LowRoll:
            def randint(self,a,b):return a
        self.c["enemy"]["hp"]=10
        outcome=game.action(self.c,"I attack the Guardian",LowRoll())
        self.assertEqual(self.c["enemy"]["phase"],2)
        self.assertIn("Bellshock",outcome["result"])
    def test_guardian_initial_attack(self):
        class LowRoll:
            def randint(self,a,b):return a
        outcome=game.action(self.c,"I attack the Guardian",LowRoll())
        self.assertEqual(self.c["enemy"]["phase"],1)
        self.assertIn("Guardian Slam",outcome["result"])
if __name__=="__main__":unittest.main()
