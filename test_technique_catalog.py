import random,unittest
import game,technique_catalog
class PathTechniqueTests(unittest.TestCase):
 def test_every_nonmage_path_covered(self):
  self.assertTrue(technique_catalog.validate())
 def test_all_paths_unlock_independently(self):
  for cls in ('Fighter','Rogue','Vessel'):
   for seed in range(50):
    h=game.character('A',22,cls,random.Random(seed))
    starting=list(h['moves'])
    game.award_experience(h,1400)
    self.assertEqual(h['level'],6)
    self.assertEqual(h['moves'],starting+technique_catalog.unlocked(h['path'],6))
    self.assertEqual(game.MOVES[h['path']],starting)
 def test_future_techniques_not_initially_known(self):
  for cls in ('Fighter','Rogue','Vessel'):
   h=game.character('A',22,cls,random.Random(2))
   self.assertTrue(set(technique_catalog.unlocked(h['path'],5)).isdisjoint(h['moves']))
