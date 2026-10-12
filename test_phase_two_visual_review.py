"""Phase 2 approved art review must identify missing replacements without generating images."""
import hashlib,tempfile,unittest
from pathlib import Path
from asset_registry import MAGIC_TYPES
import sprite_coverage

class VisualReviewAuditTests(unittest.TestCase):
 def test_missing_pack_is_flagged_not_approved(self):
  with tempfile.TemporaryDirectory() as folder:
   report=sprite_coverage.visual_review(folder)
   self.assertFalse(report['ready'])
   self.assertTrue(report['missing_portraits'])
   self.assertTrue(report['missing_bodies'])
   self.assertIn('No approved artwork pack has been installed',report['review_needed'])
 def test_empty_manifest_lists_all_class_path_art_gaps(self):
  from game import PATHS
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder)
   (root/'manifest.json').write_text('{"version":1,"assets":{}}')
   report=sprite_coverage.visual_review(root)
   self.assertEqual(len(report['missing_portraits']),sum(map(len,PATHS.values())))
   self.assertEqual(len(report['missing_bodies']),sum(map(len,PATHS.values())))
   self.assertFalse(report['ready'])
if __name__=='__main__':unittest.main()
