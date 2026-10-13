"""Phase 2 visual smoke test against actual Tk widgets and theme constants."""
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import visual_theme
import tkinter as tk
import app
import game

class PhaseTwoTabletopTest(unittest.TestCase):
 def test_readability_and_navigation_contract(self):
  palette=visual_theme.COLORS
  self.assertGreaterEqual(visual_theme.contrast(palette['ink'],palette['parchment']),7)
  self.assertGreaterEqual(visual_theme.contrast(palette['ivory'],palette['wood_dark']),7)
  self.assertEqual(len(visual_theme.NAVIGATION),9)
  self.assertEqual(len(set(visual_theme.NAVIGATION)),9)
 def test_meter_clamps_values(self):
  class FakeCanvas:
   def __init__(self):self.calls=[]
   def create_rectangle(self,*args,**kwargs):self.calls.append((args,kwargs))
  cv=FakeCanvas()
  self.assertEqual(visual_theme.meter(cv,200,100,100),98)
  self.assertEqual(visual_theme.meter(cv,-10,100,100),0)
  self.assertEqual(len(cv.calls),3)
 def test_real_party_sidebar_and_battle_widgets(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(app,'DATA',Path(folder)):
   try:window=app.App()
   except tk.TclError as exc:self.skipTest('No display: '+str(exc))
   try:
    c=game.new_campaign('Tabletop acceptance',2)
    for name,cls in [('Aster','Fighter'),('Mirae','Mage')]:
     game.add_hero(c,game.character(name,24,cls,random.Random(len(name))))
    game.start(c)
    window.c=c
    for tab in ('Record','Pack','Abilities','Journal','Story Tree','Shop','Map','Dice Board','Town'):
     window._panel(tab)
     window.update_idletasks()
     self.assertGreater(sum(isinstance(w,tk.Canvas) for w in self.walk(window)),1)
    c['enemy']={'name':'Hollow Guardian','hp':24,'max_hp':30,'ac':14,'boss':True}
    window._adventure()
    window.update_idletasks()
    labels=[w.cget('text') for w in self.walk(window) if isinstance(w,tk.Label)]
    self.assertTrue(any('ENCOUNTER' in x and 'HOLLOW GUARDIAN' in x for x in labels))
    self.assertTrue(any('HEALTH' in x for x in labels))
    self.assertTrue(any('MANA' in x for x in labels))
   finally:window.destroy()
 def walk(self,parent):
  for child in parent.winfo_children():
   yield child
   yield from self.walk(child)
if __name__=='__main__':unittest.main()
