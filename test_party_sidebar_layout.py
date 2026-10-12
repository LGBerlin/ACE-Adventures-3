import ast,unittest
from pathlib import Path
class PartySidebarLayoutTests(unittest.TestCase):
 def test_party_of_eight_and_scrollable_sidebar(self):
  src=(Path(__file__).parent/'app.py').read_text()
  app=next(n for n in ast.parse(src).body if isinstance(n,ast.ClassDef) and n.name=='App')
  funcs={n.name:ast.get_source_segment(src,n) for n in app.body if isinstance(n,ast.FunctionDef)}
  adventure=funcs['_adventure']
  sidebar=funcs['_sidebar']
  self.assertIn('row=i//4,column=i%4',adventure)
  self.assertIn('viewport=tk.Canvas(scrollregion',sidebar)
  self.assertIn('scrollregion=viewport.bbox',sidebar)
  self.assertIn('OPEN INVENTORY & EQUIPMENT',sidebar)
  self.assertIn('OPEN FULL CHARACTER SHEET',sidebar)
 def test_character_creation_shows_completed_sheet(self):
  src=(Path(__file__).parent/'app.py').read_text()
  self.assertIn('self._show();ui_character_sheet.open_sheet(self,hero)',src)
