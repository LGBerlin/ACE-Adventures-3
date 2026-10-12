import hashlib,tempfile,unittest
from pathlib import Path
from asset_registry import Registry,select_character_sprite
class SpriteSelectionTests(unittest.TestCase):
 def test_same_character_uses_same_variant(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'characters').mkdir()
   data=b'sprite-test'
   manifest={'version':1,'assets':{}}
   for i in range(3):
    p=root/'characters'/f'fighter_{i}.png';p.write_bytes(data)
    manifest['assets'][f'fighter_{i}']={'file':f'characters/fighter_{i}.png','sha256':hashlib.sha256(data).hexdigest(),'category':'portrait','tags':['class:fighter','path:knight']}
   r=Registry(root,manifest)
   hero={'class':'Fighter','path':'Knight','sprite_seed':17}
   chosen=select_character_sprite(r,hero)
   self.assertEqual(chosen,select_character_sprite(r,dict(hero)))
   self.assertIn(chosen,manifest['assets'])
 def test_path_preferred_and_class_fallback(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'characters').mkdir()
   data=b'ok'
   (root/'characters'/'rogue.png').write_bytes(data)
   entry={'file':'characters/rogue.png','sha256':hashlib.sha256(data).hexdigest(),'category':'body','tags':['class:rogue']}
   reg=Registry(root,{'version':1,'assets':{'rogue_generic':entry}})
   self.assertEqual(select_character_sprite(reg,{'class':'Rogue','path':'Ranger','sprite_seed':1},'body'),'rogue_generic')
   self.assertIsNone(select_character_sprite(reg,{'class':'Mage','path':'Runesage'},'body'))
 def test_reject_invalid_category(self):
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(ValueError):select_character_sprite(Registry(td),{'class':'Mage'},'background')
