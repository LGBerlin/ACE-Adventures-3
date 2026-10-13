import tempfile,unittest
from mage_art import MageArt,PATHS,slug
class MageArtTests(unittest.TestCase):
 def test_all_schools(self):
  self.assertEqual(len(PATHS),14)
  self.assertEqual(len(set(PATHS)),14)
  with tempfile.TemporaryDirectory() as root:
   artwork=MageArt(root)
   for path in PATHS:
    self.assertIsNone(artwork.bytes({'class':'Mage','path':path},'portrait'))
    self.assertIsNone(artwork.bytes({'class':'Mage','path':path},'character'))
 def test_other_class_and_invalid_kind(self):
  with tempfile.TemporaryDirectory() as root:
   a=MageArt(root)
   self.assertIsNone(a.bytes({'class':'Fighter','path':'Fire'},'character'))
   self.assertIsNone(a.bytes({'class':'Mage','path':'Fire'},'unknown'))
if __name__=='__main__':unittest.main()
