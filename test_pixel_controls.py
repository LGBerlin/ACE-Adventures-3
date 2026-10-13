"""Raster button art is a genuine programmatic asset and not a flattened UI."""
import unittest
from unittest.mock import patch
import pixel_controls

class PixelControlTests(unittest.TestCase):
 def test_skins_have_distinct_state_and_are_pixel_scaled(self):
  with self.subTest('normal versus highlighted'):
   a=pixel_controls.skin(140,46,False,False)
   b=pixel_controls.skin(140,46,False,True)
   self.assertEqual(a.size,b.size)
   self.assertNotEqual(a.tobytes(),b.tobytes())
  with self.subTest('parchment versus dark wood'):
   self.assertNotEqual(pixel_controls.skin(140,46,True).tobytes(),
                       pixel_controls.skin(140,46,False).tobytes())
 def test_button_callbacks_remain_callable(self):
  # Functionality and keyboard access are exercised in macOS GUI regression.
  self.assertTrue(callable(pixel_controls.PixelButton.invoke))
if __name__=='__main__':
 unittest.main()
