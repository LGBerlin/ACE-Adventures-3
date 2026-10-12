import random,unittest
import game
class CharacterRouletteSpecification(unittest.TestCase):
 def test_no_race_in_new_characters(self):
  for cls in ('Fighter','Rogue','Mage','Vessel'):
   hero=game.character('Ada',23,cls,random.Random(42))
   self.assertNotIn('race',hero)
   self.assertEqual(hero['class'],cls)
   self.assertIn('path',hero)
   self.assertIn('sprite_seed',hero)
 def test_stable_permanent_roll_data(self):
  hero=game.character('Bryn',29,'Mage',random.Random(7))
  c=game.new_campaign('Ledger',1)
  game.add_hero(c,hero)
  before=(hero['path'],hero['magic'],dict(hero['stats']),hero['sprite_seed'])
  game.start(c)
  self.assertEqual(before,(c['characters'][0]['path'],c['characters'][0]['magic'],dict(c['characters'][0]['stats']),c['characters'][0]['sprite_seed']))
