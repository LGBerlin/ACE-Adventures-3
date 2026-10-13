"""Phase 1 acceptance: complete the baseline quest via rules-owned decisions."""
import random
import tempfile
import unittest
import game
import story
import interaction

class FullCampaignJourney(unittest.TestCase):
    def setUp(self):
        self.c=game.new_campaign("The Hollow Bell acceptance",2)
        game.add_hero(self.c,game.character("Aster",24,"Fighter",random.Random(3)))
        game.add_hero(self.c,game.character("Mirae",24,"Mage",random.Random(5)))
        game.start(self.c)
    def action(self,text):
        return interaction.perform(self.c,text,random.Random(5))
    def test_npcs_clues_combat_victory_and_persistent_completion(self):
        self.assertFalse(self.action("look around")["roll_required"])
        self.assertFalse(self.action("I talk to Elder Sera")["roll_required"])
        self.assertEqual(story.ensure(self.c)["stage"],1)
        self.action("go to tavern")
        self.action("ask Mira about the bell")
        self.assertEqual(story.ensure(self.c)["stage"],2)
        self.action("go to square")
        self.action("go to well")
        self.action("examine the carvings")
        self.assertEqual(story.ensure(self.c)["stage"],3)
        self.action("go to forest")
        self.action("approach the ruined arch")
        self.assertIsNotNone(self.c["enemy"])
        self.c["enemy"]["hp"]=1
        class Certain:
            def randint(self,a,b):return b
        self.c["active"]=0
        response=interaction.perform(self.c,"I attack the guardian",Certain())
        self.assertTrue(response["roll_required"])
        self.assertIsNone(self.c["enemy"])
        self.assertEqual(story.ensure(self.c)["stage"],4)
        self.assertEqual(self.c["location"],"square")
        self.action("talk to Elder Sera")
        self.assertTrue(story.ensure(self.c)["completed"])
        with tempfile.TemporaryDirectory() as folder:
            game.save(folder,self.c)
            restored=game.load_all(folder)[0]
            self.assertTrue(restored["quest"]["completed"])
            self.assertEqual(len(restored["characters"]),2)
            self.assertTrue(restored.get("dice_history"))
    def test_no_premature_completion(self):
        with self.assertRaises(ValueError):
            self.action("go to forest")
        with self.assertRaises(ValueError):
            self.action("ask Mira about the bell")
        self.assertFalse(story.ensure(self.c)["completed"])
if __name__=="__main__":unittest.main()
