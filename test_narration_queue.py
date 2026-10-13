"""Ensure local AI latency does not discard the newest player's action."""
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import app
import game

class NarrationQueue(unittest.TestCase):
 def test_latest_pending_story_is_preserved_without_network(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(app,'DATA',Path(folder)):
   try:window=app.App()
   except tk.TclError as error:self.skipTest('No display: '+str(error))
   try:
    c=game.new_campaign('Narration audit',1)
    game.add_hero(c,game.character('Nella',24,'Fighter',random.Random(4)))
    game.start(c);window.c=c
    window.busy=True
    window._narrate('First action')
    window._narrate('Second action')
    self.assertEqual(window.pending_narration,(c['id'],'Second action'))
    self.assertEqual(c['turn'],0)
    self.assertFalse(c.get('dice_history'))
   finally:window.destroy()
if __name__=='__main__':unittest.main()
