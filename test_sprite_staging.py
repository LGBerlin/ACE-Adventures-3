import io,json,tempfile,unittest,zipfile
from pathlib import Path
from PIL import Image
from stage_sprite_candidates import stage
class SpriteStagingTests(unittest.TestCase):
 def test_nested_archive_provenance_and_limit(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);png=io.BytesIO()
   Image.new('RGBA',(64,64),(100,80,60,255)).save(png,format='PNG')
   nested=io.BytesIO()
   with zipfile.ZipFile(nested,'w') as z:
    z.writestr('goblin idle.png',png.getvalue())
    z.writestr('LICENSE.md','Author credits here')
    z.writestr('not an image.txt','ignore')
   original=root/'sprites.2.zip'
   with zipfile.ZipFile(original,'w') as z:z.writestr('sprites/monster pack.zip',nested.getvalue())
   data=stage(original,root/'staged',max_images=10)
   self.assertEqual(data['candidate_count'],1)
   self.assertEqual(data['counts']['enemy'],1)
   self.assertFalse(data['release_approved'])
   item=data['candidates'][0]
   self.assertEqual(item['pack'],'monster pack.zip')
   self.assertEqual(item['original'],'goblin idle.png')
   self.assertTrue((root/'staged'/item['file']).is_file())
   self.assertEqual(len(data['licence_documents']),1)
 def test_empty_library_not_declared_approved(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/'outer.zip'
   with zipfile.ZipFile(source,'w') as z:z.writestr('notes.txt','nothing')
   data=stage(source,root/'staged')
   self.assertEqual(data['candidate_count'],0)
   self.assertFalse(data['release_approved'])
