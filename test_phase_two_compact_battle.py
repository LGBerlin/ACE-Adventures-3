"""Phase 2 layout acceptance at the minimum supported window size."""
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import app
import game
import tabletop_layout

class CompactBattleTests(unittest.TestCase):
 def walk(self,root):
  for child in root.winfo_children():
   yield child
   yield from self.walk(child)
 def test_battle_scene_uses_less_height_than_exploration(self):
  battle=tabletop_layout.for_window(960,700,4,in_battle=True)
  normal=tabletop_layout.for_window(960,700,4,in_battle=False)
  self.assertLess(battle.scene_height,normal.scene_height)
  self.assertEqual(battle.party_columns,2)
 def test_battle_controls_are_before_story_log_and_entry_present(self):
  with tempfile.TemporaryDirectory() as directory,patch.object(app,'DATA',Path(directory)):
   try:ui=app.App()
   except tk.TclError as error:self.skipTest(str(error))
   try:
    ui.geometry('960x700');ui.update_idletasks()
    c=game.new_campaign('Compact combat',1)
    game.add_hero(c,game.character('Hero',24,'Fighter',random.Random(3)))
    game.start(c)
    c['enemy']={'name':'Hollow Guardian','hp':20,'max_hp':30,'ac':14,'boss':True}
    ui.c=c;ui._adventure();ui.update_idletasks()
    labels=[w.cget('text') for w in self.walk(ui) if isinstance(w,tk.Label)]
    self.assertIn('WHAT DO YOU DO?',labels)
    self.assertTrue(any('ENCOUNTER' in x for x in labels))
    self.assertTrue(any('ATTACK' in x for x in labels))
    text_widgets=[w for w in self.walk(ui) if isinstance(w,tk.Text)]
    self.assertEqual(len(text_widgets),1)
    self.assertEqual(int(text_widgets[0].cget('height')),3)
    self.assertTrue(any(isinstance(w,tk.Entry) for w in self.walk(ui)))
   finally:ui.destroy()
if __name__=='__main__':unittest.main()
