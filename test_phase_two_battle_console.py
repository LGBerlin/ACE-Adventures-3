"""Phase 2 encounter screen: actual Tk buttons, dice ledger and battle state."""
import random,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import app,game,dice_ledger

class BattleTabletopUi(unittest.TestCase):
 def walk(self,w):
  for item in w.winfo_children():
   yield item
   yield from self.walk(item)
 def test_battle_controls_and_roll_history_survive_panel_navigation(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(app,'DATA',Path(folder)):
   try:window=app.App()
   except tk.TclError as exc:self.skipTest('No graphics display: '+str(exc))
   try:
    c=game.new_campaign('Battle display',1)
    game.add_hero(c,game.character('Aster',24,'Fighter',random.Random(2)))
    game.start(c)
    c['enemy']={'name':'Hollow Guardian','hp':22,'max_hp':30,'ac':14,'boss':True,'phase':2}
    window.c=c
    window._adventure();window.update_idletasks()
    text=[w.cget('text') for w in self.walk(window) if isinstance(w,tk.Label)]
    for label in ('ABILITIES','POTIONS','ATTACK','GUARD','NEGOTIATE'):
     self.assertTrue(any(label in t for t in text),label)
    self.assertTrue(any('PHASE 2' in t for t in text))
    window._free('I guard')
    window._panel('Dice Board')
    window.update_idletasks()
    text=[w.cget('text') for w in self.walk(window) if isinstance(w,tk.Label)]
    self.assertIn('THE FATES · D20 LEDGER',text)
    self.assertTrue(any('D20' in t and '=' in t for t in text))
    self.assertTrue(dice_ledger.history(c))
   finally:window.destroy()
if __name__=='__main__':unittest.main()
