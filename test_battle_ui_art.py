import tempfile,unittest
from battle_ui_art import BattleUIArt
class BattleUIArtTests(unittest.TestCase):
 def test_missing_returns_none(self):
  with tempfile.TemporaryDirectory() as tmp:
   art=BattleUIArt(tmp)
   self.assertIsNone(art.button('attack'))
   self.assertIsNone(art.button('defend'))
   self.assertIsNone(art.button('end turn','disabled'))
 def test_unknown_actions_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   art=BattleUIArt(tmp)
   self.assertIsNone(art.button('open shop'))
   self.assertIsNone(art.button('attack','unknown'))
if __name__=='__main__':unittest.main()
