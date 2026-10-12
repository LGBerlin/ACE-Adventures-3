import hashlib,json,tempfile,unittest
from pathlib import Path
import game,story,update_addons
class QuestTests(unittest.TestCase):
 def campaign(self):
  c=game.new_campaign('Trial',1);game.add_hero(c,game.character('Ada',23,'Fighter'));game.start(c);return c
 def test_story_gates(self):
  c=self.campaign()
  self.assertNotIn('forest',[x for _,x in story.options(c)])
  with self.assertRaises(ValueError):story.select(c,'forest')
  story.select(c,'elder');story.select(c,'tavern');story.select(c,'mira');story.select(c,'square');story.select(c,'well');story.select(c,'runes');story.select(c,'forest');story.select(c,'encounter')
  self.assertIsNotNone(c['enemy']);self.assertEqual(story.ensure(c)['stage'],3)
 def test_addons_hash_and_rollback(self):
  with tempfile.TemporaryDirectory() as root:
   data=b'woodland palette';url='https://example.test/updates/theme.bin';manifest={'version':'1.0.1','files':[{'path':'themes/woodland.bin','url':url,'sha256':hashlib.sha256(data).hexdigest()}]}
   update_addons.apply(root,manifest,lambda u:data,'https://example.test/updates')
   self.assertEqual(json.loads((Path(root)/'addons/active.json').read_text())['version'],'1.0.1')
   self.assertEqual((Path(root)/'addons/versions/1.0.1/themes/woodland.bin').read_bytes(),data)
   update_addons.rollback(root);self.assertFalse((Path(root)/'addons/active.json').exists())
   with self.assertRaises(ValueError):update_addons.apply(root,{**manifest,'version':'1.0.2'},lambda u:b'bad','https://example.test/updates')
   self.assertFalse((Path(root)/'addons/versions/1.0.2').exists())
 def test_addons_reject_traversal(self):
  self.assertFalse(update_addons.valid_path('assets/../../config.json'))
  self.assertFalse(update_addons.valid_path('app.py'))
if __name__=='__main__':unittest.main()