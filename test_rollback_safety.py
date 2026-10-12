import json,tempfile,unittest
from pathlib import Path
from update_addons import rollback

class RollbackSafetyTests(unittest.TestCase):
 def test_existing_previous_version_restored(self):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d)/'addons'
   (base/'versions'/'1.0.0').mkdir(parents=True)
   (base/'versions'/'1.1.0').mkdir(parents=True)
   marker=base/'active.json'
   marker.write_text(json.dumps({'version':'1.1.0','previous':'1.0.0'}))
   rollback(d)
   self.assertEqual(json.loads(marker.read_text()),{'version':'1.0.0','previous':None})
 def test_missing_previous_does_not_break_active(self):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d)/'addons';base.mkdir()
   marker=base/'active.json'
   old={'version':'1.1.0','previous':'1.0.0'}
   marker.write_text(json.dumps(old))
   with self.assertRaises(ValueError):rollback(d)
   self.assertEqual(json.loads(marker.read_text()),old)
 def test_first_install_rollback_clears_pointer(self):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d)/'addons';base.mkdir()
   marker=base/'active.json';marker.write_text(json.dumps({'version':'1.0.0','previous':None}))
   rollback(d)
   self.assertFalse(marker.exists())
 def test_invalid_previous_version_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d)/'addons';base.mkdir()
   marker=base/'active.json'
   old={'version':'1.1.0','previous':'../saves'}
   marker.write_text(json.dumps(old))
   with self.assertRaises(ValueError):rollback(d)
   self.assertEqual(json.loads(marker.read_text()),old)
