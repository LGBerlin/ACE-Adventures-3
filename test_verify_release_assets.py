import json,tempfile,unittest
from pathlib import Path
from verify_release_assets import validate
class VerifiedArtworkTests(unittest.TestCase):
 def test_no_manifest_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   result=validate(d)
   self.assertFalse(result['ready'])
 def test_unreviewed_assets_fail_closed(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'manifest.json').write_text(json.dumps({'version':1,'assets':{'hero':{'file':'heroes/test.png','sha256':'0'*64,'category':'body','review':'UNREVIEWED'}}}))
   self.assertFalse(validate(p)['ready'])
 def test_empty_manifest_does_not_count_as_full_coverage(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'manifest.json').write_text(json.dumps({'version':1,'assets':{}}))
   self.assertFalse(validate(p)['ready'])
