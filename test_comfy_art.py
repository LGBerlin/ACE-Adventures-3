import json,tempfile,unittest
from pathlib import Path
import comfy_art as c
class ComfyGenerationTests(unittest.TestCase):
 def test_workflow_safe_and_pixel_style(self):
  graph=c.workflow('forest','model.safetensors',123)
  self.assertEqual(graph['5']['inputs']['seed'],123)
  self.assertIn('pixel art',graph['2']['inputs']['text'])
  self.assertEqual(graph['7']['class_type'],'SaveImage')
 def test_local_queue_history_download_and_file(self):
  calls=[]
  png=b'\x89PNG\r\n\x1a\n'+b'pretend PNG test bytes'
  def mock(url,body=None,limit=c.MAX_JSON,timeout=10):
   calls.append(url)
   if '/object_info/' in url:return json.dumps({'CheckpointLoaderSimple':{'input':{'required':{'ckpt_name':[['forest.safetensors']]}}}}).encode()
   if url.endswith('/prompt'):return json.dumps({'prompt_id':'run-1'}).encode()
   if '/history/' in url:return json.dumps({'run-1':{'outputs':{'7':{'images':[{'filename':'scene.png','subfolder':'','type':'output'}]}}}}).encode()
   if '/view?' in url:return png
   raise AssertionError(url)
  with tempfile.TemporaryDirectory() as td:
   file=c.generate('forest',td,transport=mock,poll_delay=0)
   self.assertEqual(file.read_bytes(),png)
   self.assertEqual(file.name,'forest.png')
   self.assertEqual(len(calls),4)
 def test_rejects_unknown_locations_and_missing_models(self):
  with self.assertRaises(ValueError):c.workflow('???','model.safetensors')
  def empty(url,body=None,limit=c.MAX_JSON,timeout=10):return json.dumps({'CheckpointLoaderSimple':{'input':{'required':{'ckpt_name':[[]]}}}}).encode()
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(ValueError):c.generate('square',td,transport=empty)
   self.assertFalse((Path(td)/'generated').exists())
if __name__=='__main__':unittest.main()