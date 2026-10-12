"""Exercise multiple live Tk screens, not only module imports."""
import tempfile,unittest,random
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import app,game,story

class IllustratedWindowFlow(unittest.TestCase):
 def test_party_town_inventory_forest_battle_window(self):
  with tempfile.TemporaryDirectory() as td, patch.object(app,'DATA',Path(td)):
   root=app.App()
   try:
    root.update_idletasks()
    c=game.new_campaign('Window acceptance',2)
    for name,cls in [('Aster','Fighter'),('Mirae','Mage')]:
     game.add_hero(c,game.character(name,21,cls,random.Random(len(name))))
    game.start(c);root.c=c
    for place in ['square','tavern','well','forest']:
     if place=='tavern':story.select(c,'elder');story.select(c,'tavern')
     elif place=='well':story.select(c,'mira');story.select(c,'square');story.select(c,'well')
     elif place=='forest':story.select(c,'runes');story.select(c,'forest')
     root._adventure();root.update_idletasks()
     self.assertTrue(any(isinstance(w,tk.Canvas) for w in self._walk(root)))
    root._panel('Pack');root.update_idletasks()
    root._panel('Journal');root.update_idletasks()
    root._panel('Map');root.update_idletasks()
    root._panel('Dice Board');root.update_idletasks()
    story.select(c,'encounter');root._adventure();root.update_idletasks()
    root._switch(1);root.update_idletasks()
    self.assertEqual(c['active'],1)
    self.assertTrue(c.get('enemy'))
   finally:root.destroy()
 def _walk(self,w):
  for child in w.winfo_children():
   yield child
   yield from self._walk(child)
if __name__=='__main__':unittest.main()