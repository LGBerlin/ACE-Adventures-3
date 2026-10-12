import random
import unittest
import game
import spell_catalog
import technique_catalog
class CenturyProgressionTests(unittest.TestCase):
 def test_level_cap_stats_passives_and_unlocks(self):
  for cls in game.PATHS:
   hero=game.character("Test",24,cls,random.Random(7))
   changes=game.award_experience(hero,10000)
   for step in range(500):game.award_experience(hero,10000)
   self.assertEqual(hero["level"],100)
   self.assertGreaterEqual(len(hero["passives"]),9)
   self.assertIn(hero["path"]+" Mastery 100",hero["passives"])
   expected=spell_catalog.unlocked(hero["magic"],100) if cls=="Mage" else technique_catalog.unlocked(hero["path"],100)
   self.assertTrue(set(expected).issubset(hero["moves"]))
   self.assertEqual(game.award_experience(hero,10000),[])
 def test_early_levels_do_not_grant_advanced_abilities(self):
  hero=game.character("Test",25,"Fighter",random.Random(8))
  game.award_experience(hero,1000)
  self.assertLess(hero["level"],12)
  self.assertNotIn(technique_catalog.TECHNIQUES[hero["path"]][0],hero["moves"])
 def test_rank_growth_is_not_every_level(self):
  hero=game.character("Test",25,"Fighter",random.Random(8))
  self.assertEqual(len(hero["moves"]),3)
  game.award_experience(hero,70)
  self.assertEqual(len(hero["moves"]),3)
if __name__=="__main__":unittest.main()
