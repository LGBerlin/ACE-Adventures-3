import hashlib,json,tempfile,unittest
from pathlib import Path
from update_addons import active_asset,apply,rollback
class AssetActivationTests(unittest.TestCase):
 def test_active_asset_and_rollback(self):
  with tempfile.TemporaryDirectory() as td:
   origin='https://trusted.example/releases'
   def install(version,payload):
    asset='assets/heroes/portrait.png';digest=hashlib.sha256(payload).hexdigest()
    apply(td,{'version':version,'files':[{'path':asset,'url':origin+'/'+version+'.png','sha256':digest}]},lambda url:payload,origin)
   install('1.0.0',b'FIRST')
   self.assertEqual(active_asset(td,'assets/heroes/portrait.png').read_bytes(),b'FIRST')
   install('1.0.1',b'SECOND')
   self.assertEqual(active_asset(td,'assets/heroes/portrait.png').read_bytes(),b'SECOND')
   rollback(td)
   self.assertEqual(active_asset(td,'assets/heroes/portrait.png').read_bytes(),b'FIRST')
 def test_corrupt_marker_and_traversal_are_harmless(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td)/'addons';base.mkdir()
   (base/'active.json').write_text('{broken json')
   self.assertIsNone(active_asset(td,'assets/foo.png'))
   with self.assertRaises(ValueError):active_asset(td,'../../secret')
 def test_symlink_escape_not_loaded(self):
  with tempfile.TemporaryDirectory() as td:
   b=Path(td)/'addons';v=b/'versions'/'1.0.0'/'assets';v.mkdir(parents=True)
   outside=Path(td)/'private.txt';outside.write_text('SECRET')
   (v/'portrait.png').symlink_to(outside)
   (b/'active.json').write_text(json.dumps({'version':'1.0.0'}))
   self.assertIsNone(active_asset(td,'assets/portrait.png'))
if __name__=='__main__':unittest.main()