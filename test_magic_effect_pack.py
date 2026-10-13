"""Ensure magic effects are data-driven and never bypass fallback."""
import unittest,json,tempfile
from pathlib import Path
from magic_effect_pack import Effects
class EffectRegistryTests(unittest.TestCase):
 def test_mapping_accepts_named_effects(self):
  with tempfile.TemporaryDirectory() as tmp:
   Path(tmp,'effects.json').write_text(json.dumps({'fire_impact':'effect_035.png','unsafe':'../../bad.png'}))
   found=Effects(tmp)
   self.assertEqual(found.mapping,{'fire_impact':'effect_035.png'})
   self.assertFalse(found.paint(None,'missing',0,0))
 def test_missing_index_uses_fallback(self):
  with tempfile.TemporaryDirectory() as tmp:
   self.assertFalse(Effects(tmp).paint(None,'fire_impact',0,0))
if __name__=='__main__':unittest.main()
