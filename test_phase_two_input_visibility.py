"""Capture acceptance: free-text input must remain reachable in compact windows."""
import random,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import game,app

class InputVisibility(unittest.TestCase):
 def walk(self,w):
  for c in w.winfo_children():
   yield c
   yield from self.walk(c)
 def test_exploration_and_combat_inputs_fit_visible_window(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(app,'DATA',Path(folder)):
   try:ui=app.App()
   except tk.TclError as exc:self.skipTest(str(exc))
   try:
    ui.geometry('960x680+20+35')
    c=game.new_campaign('Window fit',4)
    for i,cls in enumerate(game.PATHS):
     game.add_hero(c,game.character(cls,24,cls,random.Random(i+6)))
    game.start(c);ui.c=c
    for in_battle in (False,True):
     c['enemy']={'name':'Hollow Guardian','hp':22,'max_hp':30,'ac':14,'boss':True} if in_battle else None
     ui._adventure();ui.update_idletasks()
     entries=[w for w in self.walk(ui) if isinstance(w,tk.Entry)]
     self.assertEqual(len(entries),1)
     entry=entries[0]
     self.assertGreater(entry.winfo_height(),10)
     self.assertGreaterEqual(entry.winfo_rooty(),ui.winfo_rooty())
     self.assertLessEqual(entry.winfo_rooty()+entry.winfo_height(),ui.winfo_rooty()+ui.winfo_height())
   finally:ui.destroy()
if __name__=='__main__':unittest.main()
