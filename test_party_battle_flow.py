"""Party combat regression: actor identity, individual HP, turn effects, persistence."""
import random
import tempfile
import unittest
import combat_log
import game

class PartyBattleFlowTests(unittest.TestCase):
    def setUp(self):
        self.c=game.new_campaign("Party battle",2)
        game.add_hero(self.c,game.character("Aster",23,"Fighter",random.Random(2)))
        game.add_hero(self.c,game.character("Bryn",25,"Rogue",random.Random(3)))
        game.start(self.c)
        game.encounter(self.c,random.Random(5))
    def test_switching_party_member_changes_actor_not_others_health(self):
        a,b=self.c["characters"]
        before_b=b["hp"]
        result=game.action(self.c,"I guard",random.Random(1))
        self.assertEqual(result["hero"],"Aster")
        self.assertEqual(b["hp"],before_b)
        self.c["active"]=1
        before_a=a["hp"]
        response=game.action(self.c,"I attack the enemy",random.Random(2))
        self.assertEqual(response["hero"],"Bryn")
        self.assertEqual(a["hp"],before_a)
        self.assertEqual(self.c["turn"],2)
        actions=[r["actor"] for r in combat_log.recent(self.c) if r["kind"]=="action"]
        self.assertEqual(actions,["Aster","Bryn"])
    def test_resume_battle_preserves_active_character_and_log(self):
        self.c["active"]=1
        game.action(self.c,"I guard",random.Random(1))
        with tempfile.TemporaryDirectory() as path:
            game.save(path,self.c)
            restored=game.load_all(path)[0]
            self.assertEqual(restored["active"],1)
            self.assertIsNotNone(restored["enemy"])
            self.assertEqual(restored["combat_log"],self.c["combat_log"])
if __name__=="__main__":unittest.main()
