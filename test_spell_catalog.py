import unittest
import game,spell_catalog
class SpellCatalogTests(unittest.TestCase):
 def test_every_school_includes_exact_original_starting_names(self):
  self.assertEqual(set(spell_catalog.ADVANCED),set(game.SPELLS))
  for school,original in game.SPELLS.items():
   self.assertEqual([s['name'] for s in spell_catalog.catalog(school) if s['level']==1],original)
 def test_each_school_has_level_three_and_five_progression(self):
  for school in game.SPELLS:
   values=spell_catalog.catalog(school)
   self.assertEqual(len(values),9)
   self.assertEqual([s['level'] for s in values],[1,1,1,5,12,20,35,60,85])
   self.assertEqual(len(set(s['name'] for s in values)),9)
 def test_unlocks_are_level_gated(self):
  self.assertEqual(len(spell_catalog.unlocked('Blood',1)),3)
  self.assertEqual(len(spell_catalog.unlocked('Blood',5)),4)
  self.assertEqual(len(spell_catalog.unlocked('Blood',20)),6)
 def test_wrong_magic_rejected(self):
  with self.assertRaises(ValueError):spell_catalog.catalog('Not a school')
 def test_cleric_support_is_mage(self):
  hero={'class':'Mage','magic':'Support','path':'Spellweaver'}
  self.assertEqual(spell_catalog.role(hero),'Cleric')
