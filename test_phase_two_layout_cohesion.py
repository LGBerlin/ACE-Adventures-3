"""Adaptive layout smoke tests against both geometry and native multi-party GUI."""
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import tabletop_layout,app,game
import tkinter as tk

class LayoutCohesion(unittest.TestCase):
 def test_adaptive_geometry_is_bounded(self):
  narrow=tabletop_layout.for_window(960,700,8)
  wide=tabletop_layout.for_window(1600,1000,4)
  self.assertTrue(narrow.compact)
  self.assertEqual(narrow.party_columns,2)
  self.assertFalse(wide.compact)
  self.assertEqual(wide.party_columns,4)
  self.assertGreater(wide.scene_height,narrow.scene_height)
  self.assertIn('ENCOUNTER',tabletop_layout.scene_caption('Forest',{'name':'Guardian'}))
 def test_multi_party_screen_navigation(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(app,'DATA',Path(folder)):
   try:window=app.App()
   except tk.TclError as exc:self.skipTest('Display unavailable: '+str(exc))
   try:
    c=game.new_campaign('Tabletop layout',4)
    for cls in game.PATHS:
     game.add_hero(c,game.character(cls,24,cls,random.Random(len(cls))))
    game.start(c)
    window.c=c
    window.geometry('960x700');window.update_idletasks()
    window._adventure();window.update_idletasks()
    labels=[w.cget('text') for w in self.walk(window) if isinstance(w,tk.Label)]
    self.assertTrue(any('EXPLORING' in x for x in labels))
    window._panel('Map');window.update_idletasks()
    self.assertTrue(any(isinstance(w,tk.Canvas) for w in self.walk(window)))
    c['enemy']={'name':'Hollow Guardian','hp':25,'max_hp':30,'ac':14,'boss':True}
    window._adventure();window.update_idletasks()
    labels=[w.cget('text') for w in self.walk(window) if isinstance(w,tk.Label)]
    self.assertTrue(any('ENCOUNTER' in x for x in labels))
   finally:window.destroy()
 def walk(self,w):
  for c in w.winfo_children():
   yield c
   yield from self.walk(c)
if __name__=='__main__':unittest.main()
