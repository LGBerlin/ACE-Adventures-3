import tempfile,unittest
from vessel_art import VesselArt,slug
class VesselArtTests(unittest.TestCase):
 def test_paths(self):
  self.assertEqual(slug('Spirit Fighter'),'spirit_fighter')
  with tempfile.TemporaryDirectory() as tmp:
   a=VesselArt(tmp)
   for path in ('Monk','Spirit Fighter','Druid','Cultist','Priest'):
    self.assertIsNone(a.bytes({'class':'Vessel','path':path},'portrait'))
 def test_rejects_non_vessel_and_unknown_kind(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=VesselArt(tmp)
   self.assertIsNone(a.bytes({'class':'Mage','path':'Monk'},'character'))
   self.assertIsNone(a.bytes({'class':'Vessel','path':'Monk'},'random'))
if __name__=='__main__':unittest.main()
