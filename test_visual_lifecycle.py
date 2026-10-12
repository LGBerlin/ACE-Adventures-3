"""Stale combat effects must never appear in other characters' scenes."""
import ast,unittest
from pathlib import Path
class VisualLifecycleTests(unittest.TestCase):
 def test_navigation_clears_previous_battle_cues(self):
  source=(Path(__file__).parent/'app.py').read_text(encoding='utf-8')
  app=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='App')
  funcs={n.name:ast.get_source_segment(source,n) for n in app.body if isinstance(n,ast.FunctionDef)}
  for name in ('_home','_open','_switch','_choose'):
   self.assertIn('self.animation_director.clear()',funcs[name],name)
   self.assertIn('self.last_visual_cue=None',funcs[name],name)
 def test_encounter_completion_resets_visuals(self):
  source=(Path(__file__).parent/'app.py').read_text(encoding='utf-8')
  self.assertIn("if self.c.get('enemy') is None:self.last_visual_cue=None;self.animation_director.clear()",source)
