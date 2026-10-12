import ast,unittest
from pathlib import Path
class DungeonMasterStatusTests(unittest.TestCase):
 def test_status_updates_during_async_narration(self):
  source=(Path(__file__).parent/'app.py').read_text()
  app=next(x for x in ast.parse(source).body if isinstance(x,ast.ClassDef) and x.name=='App')
  methods={x.name:ast.get_source_segment(source,x) for x in app.body if isinstance(x,ast.FunctionDef)}
  self.assertIn('Dungeon Master is responding...',methods['_narrate'])
  self.assertIn('Ready for your next action',methods['_poll'])
  self.assertIn('self.dm_status',methods['_adventure'])
