"""Visual consistency and approved sprite fallback integration tests."""
import hashlib,random,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from io import BytesIO
from PIL import Image
import asset_registry,game

def png(color):
 image=Image.new('RGBA',(64,64),color)
 out=BytesIO();image.save(out,format='PNG')
 return out.getvalue()

class SpriteConsistencyTests(unittest.TestCase):
 def test_corrupt_path_art_uses_class_fallback(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'characters').mkdir()
   good=png((80,110,150,255))
   (root/'characters'/'fighter.png').write_bytes(good)
   (root/'characters'/'knight.png').write_bytes(b'corrupt')
   spec={'version':1,'assets':{
    'path_knight':{'file':'characters/knight.png','sha256':hashlib.sha256(good).hexdigest(),'category':'body','tags':['class:fighter','path:knight']},
    'class_fighter':{'file':'characters/fighter.png','sha256':hashlib.sha256(good).hexdigest(),'category':'body','tags':['class:fighter']}}}
   registry=asset_registry.Registry(root,spec)
   hero={'class':'Fighter','path':'Knight','sprite_seed':31}
   self.assertEqual(asset_registry.select_character_sprite(registry,hero,'body'),'class_fighter')
 def test_actual_combat_prefers_approved_image(self):
  import tkinter as tk
  import app
  with tempfile.TemporaryDirectory() as folder,patch.object(app,'DATA',Path(folder)):
   try:window=app.App()
   except tk.TclError as exc:self.skipTest('No Tk display: '+str(exc))
   try:
    c=game.new_campaign('Sprite proof',1)
    hero=game.character('Eira',24,'Fighter',random.Random(4))
    game.add_hero(c,hero);game.start(c)
    c['enemy']={'name':'Thorn Wolf','hp':15,'max_hp':15,'ac':12}
    window.c=c
    root=Path(folder)/'approved sprites';(root/'characters').mkdir(parents=True)
    payload=png((40,160,90,255))
    (root/'characters'/'fighter.png').write_bytes(payload)
    window.asset_pack=asset_registry.Registry(root,{'version':1,'assets':{
     'hero_body':{'file':'characters/fighter.png','sha256':hashlib.sha256(payload).hexdigest(),
                  'category':'body','tags':['class:fighter']}}})
    window._adventure();window.update_idletasks()
    canvases=[cv for cv in self.walk(window) if isinstance(cv,tk.Canvas)]
    self.assertTrue(any(getattr(cv,'_ace_characters',None) for cv in canvases))
   finally:window.destroy()
 def walk(self,widget):
  for child in widget.winfo_children():
   yield child
   yield from self.walk(child)
if __name__=='__main__':unittest.main()
