"""Phase 2 journal, story-tree and enchanting-wheel UI acceptance."""
import random,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import app,game,story

class VisualChronicleTests(unittest.TestCase):
 def widgets(self,widget):
  for child in widget.winfo_children():
   yield child
   yield from self.widgets(child)
 def test_chronicle_screens_and_enchant_ring(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(app,'DATA',Path(folder)):
   try:window=app.App()
   except tk.TclError as exc:self.skipTest('Tk display unavailable: '+str(exc))
   try:
    c=game.new_campaign('Visual Chronicle',1)
    game.add_hero(c,game.character('Lyra',24,'Mage',random.Random(3)))
    game.start(c);story.ensure(c)
    c['history'].extend(['The lanterns flicker.','The guild captain waits.'])
    window.c=c
    for tab,heading in [('Journal','CHRONICLE · QUEST JOURNAL'),('Story Tree','THE HOLLOW BELL · CHRONICLE')]:
     window._panel(tab);window.update_idletasks()
     labels=[w.cget('text') for w in self.widgets(window) if isinstance(w,tk.Label)]
     self.assertIn(heading,labels)
    c['last_enchant_spin']={'item':'Mystic Robe','slot':2,'outcome':'Storm','level':1}
    window._enchant_wheel()
    window.update_idletasks()
    popups=[w for w in window.winfo_children() if isinstance(w,tk.Toplevel)]
    self.assertTrue(popups)
    canvas=next(w for w in self.widgets(popups[-1]) if isinstance(w,tk.Canvas))
    self.assertGreater(len(canvas.find_all()),12)
    popups[-1].destroy()
   finally:window.destroy()
if __name__=='__main__':unittest.main()
