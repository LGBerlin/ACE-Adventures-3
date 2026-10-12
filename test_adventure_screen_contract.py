import ast,unittest
from pathlib import Path
class AdventureScreenContractTests(unittest.TestCase):
 def setUp(self):
  self.source=(Path(__file__).parent/'app.py').read_text(encoding='utf-8')
  app=next(n for n in ast.parse(self.source).body if isinstance(n,ast.ClassDef) and n.name=='App')
  self.methods={n.name:ast.get_source_segment(self.source,n) for n in app.body if isinstance(n,ast.FunctionDef)}
 def test_freeform_only_primary_interaction(self):
  screen=self.methods['_adventure']
  self.assertIn("'WHAT DO YOU DO?'",screen)
  self.assertIn("'SEND ACTION'",screen)
  self.assertNotIn("story.options(self.c)",screen)
  self.assertIn("self._sidebar(right)",screen)
 def test_party_and_navigation_visible(self):
  screen=self.methods['_adventure']
  self.assertIn("'Your party'",screen)
  sidebar=self.methods['_sidebar']
  import visual_theme
  self.assertIn('visual_theme.NAVIGATION',sidebar)
  for label in ('Character Sheet','Inventory','Abilities','Journal','Story Tree'):
   self.assertIn(label,visual_theme.NAVIGATION)
 def test_roll_only_on_checked_action(self):
  handler=self.methods['_free']
  self.assertIn("interaction.perform(self.c,text)",handler)
  self.assertIn("if result['roll_required']:self._roll_display(result)",handler)
 def test_controls_are_explicitly_painted(self):
  button=self.methods['button']
  self.assertIn('tk.Label(',button)
  self.assertIn("fg=fg",button)
  self.assertIn("bg=bg",button)
