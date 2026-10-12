import random,unittest
import tkinter as tk
import game,ui_abilities
class AbilitiesUITests(unittest.TestCase):
 def test_every_path_and_magic_type_has_full_folio_entries(self):
  for cls in game.PATHS:
   for seed in range(40):
    h=game.character('Hero',24,cls,random.Random(seed))
    items=ui_abilities.entries(h)
    self.assertGreaterEqual(len(items),5)
    self.assertTrue(all('name' in item and 'level' in item for item in items))
 def test_live_spellbook_and_technique_windows(self):
  try:root=tk.Tk()
  except tk.TclError as e:self.skipTest(str(e))
  root.withdraw()
  try:
   for cls in ('Mage','Rogue','Fighter','Vessel'):
    h=game.character('Hero',24,cls,random.Random(1))
    win=ui_abilities.open_abilities(root,h)
    root.update_idletasks()
    self.assertGreater(win.winfo_width(),500)
    win.destroy()
  finally:root.destroy()
