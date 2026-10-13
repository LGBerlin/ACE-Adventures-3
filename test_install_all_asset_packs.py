"""Smoke tests for the consolidated asset installer."""
import tempfile,unittest,zipfile
from pathlib import Path
from install_all_asset_packs import PAIRS,install

class CombinedArtInstallTests(unittest.TestCase):
 def test_every_existing_registry_has_installer_target(self):
  expected={'fighter art','rogue art','vessel art','mage art','npc art',
            'battle ui','magic effects','battle effects','utility ui',
            'character sheet ui','overall ui','items','enemies','ui sprites'}
  self.assertEqual(set(folder for folder,_ in PAIRS.values()),expected)
 def test_incomplete_bundle_rejected_without_changes(self):
  with tempfile.TemporaryDirectory() as temp:
   archive=Path(temp)/'empty.zip'
   with zipfile.ZipFile(archive,'w') as z:
    z.writestr('bundle manifest.json','{"packages":{}}')
   destination=Path(temp)/'application'
   with self.assertRaises(ValueError):install(archive,destination)
   self.assertFalse(any(destination.glob('*')))

if __name__=='__main__':unittest.main()
