import random,unittest
import game
from spell_catalog import catalog
class ExperienceSpellTests(unittest.TestCase):
 def test_mage_earns_regular_spell_at_level_five(self):
  hero=game.character('Iris',25,'Mage',random.Random(2))
  school=hero['magic']
  first=tuple(hero['moves'])
  game.award_experience(hero,82)
  self.assertEqual(hero['level'],2)
  self.assertEqual(tuple(hero['moves']),first)
  names=game.award_experience(hero,188)
  self.assertEqual(hero['level'],3)
  self.assertEqual(names,[])
  names=game.award_experience(hero,790)
  self.assertEqual(hero['level'],5)
  self.assertIn(catalog(school)[3]['name'],names)
 def test_no_duplicates_on_additional_awards(self):
  hero=game.character('Iris',25,'Mage',random.Random(8))
  game.award_experience(hero,1000)
  before=set(hero['moves'])
  game.award_experience(hero,1000)
  self.assertTrue(before.issubset(set(hero['moves'])))
  self.assertEqual(len(hero['moves']),len(set(hero['moves'])))
 def test_xp_validation_and_non_mage(self):
  hero=game.character('Ada',24,'Fighter',random.Random(4))
  with self.assertRaises(ValueError):game.award_experience(hero,-1)
  with self.assertRaises(ValueError):game.award_experience(hero,True)
  game.award_experience(hero,500)
  import technique_catalog
  self.assertEqual(hero['moves'],game.MOVES[hero['path']]+technique_catalog.unlocked(hero['path'],hero['level']))
