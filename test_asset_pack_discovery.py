"""Approved sprite pack lookup for source, installed and frozen app."""
import tempfile
import unittest
from pathlib import Path
from asset_registry import find_approved_assets

class PackLookupTests(unittest.TestCase):
 def test_bundled_approved_manifest_is_discovered(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   data=root/'home'
   base=root/'bundle'
   pack=base/'assets'/'approved sprites'
   pack.mkdir(parents=True)
   (pack/'manifest.json').write_text('{"version":1,"assets":{}}')
   self.assertEqual(find_approved_assets(data,base),pack)
 def test_user_override_precedence(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);data=root/'home'
   installed=data/'approved sprites';installed.mkdir(parents=True)
   (installed/'manifest.json').write_text('{"version":1,"assets":{}}')
   bundle=root/'bundle'/'assets'/'approved sprites'
   bundle.mkdir(parents=True)
   (bundle/'manifest.json').write_text('{"version":1,"assets":{}}')
   self.assertEqual(find_approved_assets(data,root/'bundle'),installed)
 def test_no_manifest_falls_back_without_claiming_approval(self):
  with tempfile.TemporaryDirectory() as tmp:
   data=Path(tmp)/'home'
   self.assertEqual(find_approved_assets(data,Path(tmp)/'bundle'),data/'approved sprites')
if __name__=='__main__':unittest.main()
