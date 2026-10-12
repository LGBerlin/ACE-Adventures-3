import tempfile,unittest
from pathlib import Path
import game
from sprite_coverage import report,CLASS_CORE
from asset_registry import MAGIC_TYPES
class SpriteCoverageTests(unittest.TestCase):
 def test_class_paths_and_moves(self):
  self.assertEqual(sum(len(p) for p in game.PATHS.values()),17)
  for cls,paths in game.PATHS.items():
   for path in paths:
    hero=game.character('A',20,cls)
    self.assertIn(path,game.MOVES if cls!='Mage' else game.PATHS[cls])
    self.assertTrue(path in game.MOVES or cls=='Mage')
 def test_magic_registry(self):
  self.assertEqual(len(game.SPELLS),14)
  self.assertEqual(set(game.SPELLS),set(MAGIC_TYPES))
 def test_missing_art_does_not_appear_ready(self):
  with tempfile.TemporaryDirectory() as t:
   r=report(Path(t))
   self.assertFalse(r['ready'])
   self.assertEqual(r['asset_count'],0)
