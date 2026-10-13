import random
import tempfile
import unittest
import combat_log
import game
class CombatLogTests(unittest.TestCase):
    def setUp(self):
        self.c=game.new_campaign("Combat ledger",2)
        for name in ("Aster","Mira"):
            game.add_hero(self.c,game.character(name,23,"Fighter",random.Random(len(name))))
        game.start(self.c)
    def test_party_attack_is_logged_with_real_actor(self):
        game.encounter(self.c,random.Random(1))
        self.c["active"]=1
        game.action(self.c,"I attack the enemy",random.Random(7))
        records=combat_log.recent(self.c)
        self.assertTrue(any(e["actor"]=="Mira" and e["kind"]=="action" for e in records))
        with tempfile.TemporaryDirectory() as folder:
            game.save(folder,self.c)
            self.assertEqual(game.load_all(folder)[0]["combat_log"],self.c["combat_log"])
    def test_bounded_and_safe(self):
        for i in range(75):
            combat_log.append(self.c,actor="Aster",kind="action",description="x"*1000)
        self.assertEqual(len(combat_log.recent(self.c,100)),60)
        self.assertEqual(len(combat_log.recent(self.c)[-1]["description"]),600)
    def test_read_does_not_mutate(self):
        self.assertEqual(combat_log.recent(self.c),[])
        self.assertNotIn("combat_log",self.c)
if __name__=="__main__":unittest.main()
