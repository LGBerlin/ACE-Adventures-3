"""The tabletop dice tray must show the rules ledger, not invent rolls."""
import ast
import unittest
from pathlib import Path

class DiceTrayContract(unittest.TestCase):
 def test_tray_is_visual_only(self):
  source=(Path(__file__).parent/'app.py').read_text(encoding='utf-8')
  tree=ast.parse(source)
  app=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='App')
  tray=next(x for x in app.body if isinstance(x,ast.FunctionDef) and x.name=='_dice_tray')
  code=ast.get_source_segment(source,tray)
  self.assertIn('dice_ledger.history(self.c)',code)
  self.assertIn("row['roll']",code)
  self.assertNotIn('random.',code)
  self.assertNotIn('dice_ledger.record(',code)
  self.assertNotIn('game.save(',code)
 def test_adventure_invokes_tray(self):
  source=(Path(__file__).parent/'app.py').read_text(encoding='utf-8')
  self.assertIn('self._dice_tray(f)',source)
if __name__=='__main__':unittest.main()
