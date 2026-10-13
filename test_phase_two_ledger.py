"""Phase 2 real-Tk acceptance for scrollable parchment ledger and equipment panels."""
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import app,game,merchant

class TabletopLedgerTests(unittest.TestCase):
 def walk(self,widget):
  for child in widget.winfo_children():
   yield child
   yield from self.walk(child)
 def test_sidebar_stays_navigable_with_long_lists(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(app,'DATA',Path(folder)):
   try:window=app.App()
   except tk.TclError as error:self.skipTest('No Tk display: '+str(error))
   try:
    c=game.new_campaign('Ledger UI',1)
    game.add_hero(c,game.character('Aster',24,'Fighter',random.Random(4)))
    game.start(c)
    window.c=c
    c['characters'][0]['inventory']+=['Health Potion']*20
    c['location']='market'
    for tab in ('Record','Pack','Abilities','Shop','Town'):
     window._panel(tab);window.update_idletasks()
     widgets=list(self.walk(window))
     labels=[w.cget('text') for w in widgets if isinstance(w,tk.Label)]
     self.assertTrue(any('Aster' in label for label in labels),tab)
     self.assertGreaterEqual(len([w for w in widgets if isinstance(w,tk.Scrollbar)]),2,tab)
     self.assertTrue(any('◆' in label for label in labels),tab)
    window._panel('Record');window.update_idletasks()
    text=[w.cget('text') for w in self.walk(window) if isinstance(w,tk.Label)]
    self.assertIn('CHARACTER PROFILE',text)
    self.assertIn('ATTRIBUTES',text)
    self.assertIn('EQUIPMENT',text)
    window._panel('Shop');window.update_idletasks()
    text=[w.cget('text') for w in self.walk(window) if isinstance(w,tk.Label)]
    self.assertIn('SUPPLIES & SCROLLS',text)
    self.assertIn('WEAPON',text)
    self.assertIn('ARMOR',text)
   finally:window.destroy()
if __name__=='__main__':unittest.main()
