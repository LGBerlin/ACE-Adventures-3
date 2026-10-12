"""Live Mac acceptance for the parchment character sheet."""
import random,tempfile,unittest
import tkinter as tk
import game,ui_character_sheet

class CharacterSheetUITests(unittest.TestCase):
 def test_open_sheet_contains_all_attributes_and_sections(self):
  try:root=tk.Tk()
  except tk.TclError as e:self.skipTest(str(e))
  root.withdraw()
  try:
   hero=game.character('Arlen',29,'Mage',random.Random(5))
   win=ui_character_sheet.open_sheet(root,hero)
   root.update_idletasks()
   labels=[]
   def collect(w):
    for ch in w.winfo_children():
     if isinstance(ch,tk.Label):labels.append(ch.cget('text'))
     collect(ch)
   collect(win)
   combined=' '.join(labels)
   for entry in ('STR','DEX','CON','INT','WIS','CHA','INVENTORY','ABILITIES','29','Arlen'):
    self.assertIn(entry,combined)
   self.assertGreater(win.winfo_width(),450)
   win.destroy()
  finally:root.destroy()
