"""Phase 2 keyboard focus, hover and sidebar scroll control acceptance."""
import random,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import app,game

class AccessibleTabletop(unittest.TestCase):
 def walk(self,parent):
  for child in parent.winfo_children():
   yield child
   yield from self.walk(child)
 def test_buttons_have_keyboard_focus_and_scrolling_sidebar(self):
  with tempfile.TemporaryDirectory() as td,patch.object(app,'DATA',Path(td)):
   try:ui=app.App()
   except tk.TclError as exc:self.skipTest(str(exc))
   try:
    c=game.new_campaign('Interaction QA',1)
    game.add_hero(c,game.character('Hero',24,'Fighter',random.Random(3)))
    game.start(c);ui.c=c
    ui._panel('Abilities');ui.update_idletasks()
    widgets=list(self.walk(ui))
    buttons=[w for w in widgets if isinstance(w,tk.Label) and str(w.cget('takefocus'))=='1']
    self.assertTrue(buttons)
    bindings=buttons[0].bind()
    self.assertIn('<FocusIn>',bindings)
    self.assertIn('<Return>',bindings)
    self.assertIn('<Enter>',bindings)
    scrollers=[w for w in widgets if isinstance(w,tk.Canvas) and '<MouseWheel>' in w.bind()]
    self.assertTrue(scrollers)
    before=c['turn']
    scrollers[0].event_generate('<MouseWheel>',delta=-120)
    ui.update_idletasks()
    self.assertEqual(c['turn'],before)
   finally:ui.destroy()
if __name__=='__main__':unittest.main()
