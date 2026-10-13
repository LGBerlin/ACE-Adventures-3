import unittest,tempfile
from pathlib import Path
from fighter_art import FighterArt,slug,PATHS

class FighterArtworkTests(unittest.TestCase):
 def test_path_alias(self):
  self.assertEqual(slug('Martial Artist'),'martial_artist')
  self.assertEqual(slug('Dual Sword'),'dual_sword')
 def test_missing_pack_is_safe(self):
  with tempfile.TemporaryDirectory() as tmp:
   art=FighterArt(tmp)
   for path in ('Martial Artist','Knight','Barbarian','Paladin','Swordsman'):
    self.assertIsNone(art.bytes({'class':'Fighter','path':path},'portrait'))
    self.assertIsNone(art.bytes({'class':'Fighter','path':path},'character'))
 def test_does_not_mix_classes(self):
  with tempfile.TemporaryDirectory() as tmp:
   self.assertIsNone(FighterArt(tmp).bytes({'class':'Mage','path':'Knight'},'portrait'))
 def test_five_path_coverage(self):
  self.assertEqual(len(PATHS),5)
if __name__=='__main__':unittest.main()
