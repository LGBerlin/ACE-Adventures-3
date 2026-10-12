import unittest
from visual_mapping import cue_for

class DiceAnimationOutcomeTests(unittest.TestCase):
 def test_failed_attack_no_impact(self):
  result=cue_for({'class':'Fighter'},{'action':'I slash at the goblin','degree':'Failure'})
  self.assertEqual(result['animation'],'attack')
  self.assertIsNone(result['effect'])
 def test_successful_attack_has_impact(self):
  result=cue_for({'class':'Rogue'},{'action':'I stab the goblin','degree':'Success'})
  self.assertEqual(result['effect'],'physical_impact')
 def test_failed_spell_no_impact(self):
  result=cue_for({'class':'Mage','magic':'Fire'},{'action':'I cast a fire spell','degree':'Critical Failure'})
  self.assertEqual(result['animation'],'cast')
  self.assertIsNone(result['effect'])
 def test_successful_fire_uses_element(self):
  result=cue_for({'class':'Mage','magic':'Fire'},{'action':'I cast a fire spell','degree':'Success'})
  self.assertEqual(result['effect'],'fire_impact')
