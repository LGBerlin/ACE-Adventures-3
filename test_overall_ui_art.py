import tempfile,unittest
from overall_ui_art import OverallUIArt
class OverallUIArtTests(unittest.TestCase):
 def test_safe_fallback(self):
  with tempfile.TemporaryDirectory() as root:
   art=OverallUIArt(root)
   self.assertIsNone(art.read('speaker_narrator'))
   self.assertIsNone(art.read('unknown_art'))
   self.assertIsNone(art.read('dialogue_log_example'))
if __name__=='__main__':unittest.main()
