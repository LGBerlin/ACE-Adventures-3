import ast,unittest
from pathlib import Path

class ContentRecoveryInterfaceTests(unittest.TestCase):
 def test_recovery_action_is_visible(self):
  text=(Path(__file__).parent/'app.py').read_text()
  self.assertIn("'RESTORE PREVIOUS CONTENT',self._rollback_content",text)
  self.assertIn("update_addons.rollback(DATA)",text)
 def test_recovery_does_not_remove_campaigns(self):
  text=(Path(__file__).parent/'app.py').read_text()
  tree=ast.parse(text)
  app=next(c for c in tree.body if isinstance(c,ast.ClassDef) and c.name=='App')
  rollback=next(n for n in app.body if isinstance(n,ast.FunctionDef) and n.name=='_rollback_content')
  body=ast.get_source_segment(text,rollback)
  self.assertNotIn('game.save(',body)
  self.assertNotIn('shutil.rmtree',body)
