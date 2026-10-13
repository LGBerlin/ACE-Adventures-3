import tempfile,unittest
from pathlib import Path
from rogue_art import RogueArt
class RogueArtTests(unittest.TestCase):
 def test_missing_asset_returns_none(self):
  with tempfile.TemporaryDirectory() as root:
   art=RogueArt(root)
   for path in ('Thief','Ranger','Assassin','Arcane Trickster'):
    self.assertIsNone(art.bytes({'class':'Rogue','path':path},'portrait'))
 def test_other_classes_not_affected(self):
  with tempfile.TemporaryDirectory() as root:
   self.assertIsNone(RogueArt(root).bytes({'class':'Fighter','path':'Ranger'},'sprite'))
if __name__=='__main__':unittest.main()
