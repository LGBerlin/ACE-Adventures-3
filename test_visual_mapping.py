import unittest
from visual_mapping import cue_for,MAGIC_EFFECTS,CLASS_ATTACKS
from asset_registry import MAGIC_TYPES,CLASSES
class VisualMappingTests(unittest.TestCase):
 def test_all_schools(self):
  self.assertEqual(set(MAGIC_EFFECTS),set(MAGIC_TYPES))
  for magic in MAGIC_TYPES:
   result=cue_for({'class':'Mage','magic':magic},{'action':'I cast a magic spell'})
   self.assertEqual(result['animation'],'cast')
   self.assertTrue(result['effect'])
 def test_all_classes(self):
  self.assertEqual(set(CLASS_ATTACKS),set(CLASSES))
  for cls in CLASSES:
   self.assertEqual(cue_for({'class':cls},{'action':'I attack'})['animation'],'attack')
 def test_guard_does_not_attack(self):
  self.assertEqual(cue_for({'class':'Fighter'},{'action':'I shield and attack'})['animation'],'guard')
 def test_unknowns_are_bounded(self):
  self.assertEqual(cue_for({'class':'Nonexistent'},{'action':'look around'})['animation'],'idle')
