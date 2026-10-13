"""Phase 2 visible sidebar panel acceptance on a 1024x768 Mac display."""
import random,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import app,game

class SidebarVisibility(unittest.TestCase):
 def walk(self,w):
  for child in w.winfo_children():
   yield child
   yield from self.walk(child)
 def test_selected_panel_is_visible_below_compact_portrait(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(app,'DATA',Path(folder)):
   try:ui=app.App()
   except tk.TclError as exc:self.skipTest(str(exc))
   try:
    ui.geometry('960x700+20+25')
    c=game.new_campaign('Visibility',1)
    game.add_hero(c,game.character('Lyra',24,'Mage',random.Random(5)))
    game.start(c);ui.c=c;c['location']='market'
    for panel,term in [('Pack','ADVENTURER’S PACK'),('Shop','PURSE'),('Town','ACTIVE QUESTS'),('Map','PARCHMENT ATLAS'),('Story Tree','THE HOLLOW BELL · CHRONICLE')]:
     ui._panel(panel);ui.update_idletasks()
     matches=[w for w in self.walk(ui) if isinstance(w,tk.Label) and term in w.cget('text')]
     self.assertTrue(matches,panel)
     item=matches[0]
     self.assertGreater(item.winfo_height(),3,panel)
     self.assertLess(item.winfo_rooty(),ui.winfo_rooty()+ui.winfo_height()-15,panel)
     if panel=='Map':
      maps=[w for w in self.walk(ui) if isinstance(w,tk.Canvas) and int(w.cget('width'))==274]
      self.assertTrue(maps)
      self.assertLess(maps[0].winfo_rooty(),ui.winfo_rooty()+ui.winfo_height()-15)
   finally:ui.destroy()
if __name__=='__main__':unittest.main()
