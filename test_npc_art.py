import tempfile, unittest
from npc_art import NPCArt
class NPCArtTests(unittest.TestCase):
 def test_missing_and_unknown_roles(self):
  with tempfile.TemporaryDirectory() as folder:
   art=NPCArt(folder)
   self.assertIsNone(art.bytes('merchant'))
   self.assertIsNone(art.bytes('apothecary','character'))
   self.assertIsNone(art.bytes('something else'))
   self.assertIsNone(art.bytes('merchant','unapproved'))
if __name__=='__main__':unittest.main()
