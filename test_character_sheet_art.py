import tempfile,unittest
from character_sheet_art import CharacterSheetArt
class CharacterSheetArtTests(unittest.TestCase):
 def test_tabs_and_missing_fallback(self):
  with tempfile.TemporaryDirectory() as directory:
   art=CharacterSheetArt(directory)
   for panel in ('Record','Pack','Abilities'):
    self.assertIsNone(art.tab(panel))
   self.assertIsNone(art.tab('Combat'))
   self.assertIsNone(art.read('invalid'))
if __name__=='__main__':unittest.main()
