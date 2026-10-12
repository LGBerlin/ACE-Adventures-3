import hashlib,tempfile,unittest
from pathlib import Path
from asset_registry import Registry,appearance_id,MAGIC_TYPES

class SpriteRegistryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.root=Path(self.tmp.name)
  (self.root/'heroes').mkdir()
  self.a=b'one';self.b=b'two';self.c=b'three'
  for name,body in [('one',self.a),('two',self.b),('three',self.c)]:
   (self.root/'heroes'/(name+'.png')).write_bytes(body)
  self.entries={k:{'file':'heroes/'+k+'.png','sha256':hashlib.sha256(v).hexdigest(),'category':'body','tags':['class:fighter']} for k,v in [('one',self.a),('two',self.b),('three',self.c)]}
 def tearDown(self):self.tmp.cleanup()
 def test_load_and_select(self):
  reg=Registry(self.root,{'version':1,'assets':self.entries},max_cache_bytes=6)
  self.assertEqual(reg.choose('body',**{'class':'fighter'}),['one','three','two'])
  self.assertEqual(reg.bytes('one'),self.a)
 def test_cache_budget_eviction(self):
  reg=Registry(self.root,{'version':1,'assets':self.entries},max_cache_bytes=5)
  reg.bytes('one');reg.bytes('two');reg.bytes('three')
  self.assertLessEqual(reg.cache_size,5)
  self.assertNotIn('one',reg.cache)
 def test_checksum_tamper_ignored(self):
  reg=Registry(self.root,{'version':1,'assets':self.entries})
  (self.root/'heroes'/'one.png').write_bytes(b'changed')
  self.assertIsNone(reg.bytes('one'))
 def test_reject_bad_path(self):
  for value in ('../private.png','heroes/../../secret.png','/tmp/a.png','heroes/file.py','heroes\\one.png'):
   entry=dict(self.entries['one'],file=value)
   with self.subTest(value=value),self.assertRaises(ValueError):
    Registry(self.root,{'version':1,'assets':{'bad':entry}})
 def test_symlink_escape(self):
  with tempfile.TemporaryDirectory() as outside:
   (Path(outside)/'bad.png').write_bytes(b'outside')
   (self.root/'heroes'/'escape.png').symlink_to(Path(outside)/'bad.png')
   reg=Registry(self.root,{'version':1,'assets':{'escape':dict(self.entries['one'],file='heroes/escape.png')}})
   self.assertIsNone(reg.bytes('escape'))
 def test_stable_appearance(self):
  c={'name':'Ada','class':'Mage','sprite_seed':1234}
  self.assertEqual(appearance_id(c),appearance_id(dict(c)))
  self.assertNotEqual(appearance_id(c),appearance_id(dict(c,sprite_seed=42)))
 def test_all_magic_schools_registered(self):
  self.assertEqual(len(MAGIC_TYPES),14)
