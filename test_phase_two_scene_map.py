"""Phase 2 canvas presentation acceptance: distinct opponents, map, and scene bounds."""
import random,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import game,app,art

class SceneAndMapTest(unittest.TestCase):
 def all_widgets(self,w):
  for c in w.winfo_children():
   yield c
   yield from self.all_widgets(c)
 def test_distinct_enemy_silhouettes_have_no_external_assets(self):
  class FakeCanvas:
   def __init__(self):self.calls=[]
   def __getattr__(self,name):
    if name.startswith('create_'):
     def draw(*args,**kwargs):self.calls.append((name,args,kwargs))
     return draw
    raise AttributeError(name)
  for name,wanted in [('Hollow Guardian','guardian'),('Thorn Wolf','wolf'),('Forest Wisp','wisp'),('Moss Goblin','goblin')]:
   canvas=FakeCanvas()
   with self.subTest(name=name):
    self.assertEqual(art.enemy(canvas,180,140,name,7,2),wanted)
    self.assertGreater(len(canvas.calls),3)
 def test_live_battle_and_map_render_into_actual_canvas(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(app,'DATA',Path(folder)):
   try:window=app.App()
   except tk.TclError as exc:self.skipTest('No display: '+str(exc))
   try:
    c=game.new_campaign('Illustrated scene',1)
    game.add_hero(c,game.character('Arin',25,'Fighter',random.Random(2)))
    game.start(c)
    c['enemy']={'name':'Hollow Guardian','hp':22,'max_hp':30,'ac':14,'boss':True}
    window.c=c;window._adventure();window.update_idletasks()
    scene=next(cv for cv in self.all_widgets(window) if isinstance(cv,tk.Canvas) and cv.winfo_width()>400)
    window._scene(scene,'forest')
    self.assertGreater(len(scene.find_all()),10)
    self.assertTrue(any('Hollow Guardian' in str(scene.itemcget(item,'text')) for item in scene.find_withtag('all')))
    c['enemy']=None;c['location']='square'
    window._panel('Map');window.update_idletasks()
    maps=[cv for cv in self.all_widgets(window) if isinstance(cv,tk.Canvas) and 'place_square' in cv.gettags('place_square')]
    self.assertTrue(maps)
    self.assertTrue(maps[0].find_withtag('place_market'))
   finally:window.destroy()
if __name__=='__main__':unittest.main()
