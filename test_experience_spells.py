import random,unittest
import game
from spell_catalog import catalog
class ExperienceSpellTests(unittest.TestCase):
 def test_mage_earns_new_spells_at_level_three_and_five(self):
  hero=game.character('Iris',25,'Mage',random.Random(2))
  school=hero['magic']
  first=tuple(hero['moves'])
  game.award_experience(hero,50)
  self.assertEqual(hero['level'],2)
  self.assertEqual(tuple(hero['moves']),first)
  names=game.award_experience(hero,100)
  self.assertEqual(hero['level'],3)
  self.assertEqual(names,[catalog(school)[3]['name']])
  names=game.award_experience(hero,450)
  self.assertEqual(hero['level'],5)
  self.assertIn(catalog(school)[4]['name'],names)
 def test_no_duplicates_on_additional_awards(self):
  hero=game.character('Iris',25,'Mage',random.Random(8))
  game.award_experience(hero,1000)
  before=list(hero['moves'])
  game.award_experience(hero,1000)
  self.assertEqual(hero['moves'],before)
 def test_xp_validation_and_non_mage(self):
  hero=game.character('Ada',24,'Fighter',random.Random(4))
  with self.assertRaises(ValueError):game.award_experience(hero,-1)
  with self.assertRaises(ValueError):game.award_experience(hero,True)
  game.award_experience(hero,500)
  self.assertEqual(hero['moves'],game.MOVES[hero['path']])
