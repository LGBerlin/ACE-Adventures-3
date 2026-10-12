"""Cross-system Phase 1 acceptance: quest travel, saves, updates, rollback.

All updates are mocked byte-for-byte. No network dependency, no writes to app code.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import game
import story
import town_services
import addon_updates
import update_addons

class JourneyAndUpdaterIntegration(unittest.TestCase):
 def make(self):
  c=game.new_campaign('Cross-system acceptance',1)
  game.add_hero(c,game.character('Tester',23,'Fighter'))
  game.start(c)
  return c
 def test_guild_needs_actual_travel_and_return_and_survives_reload(self):
  with tempfile.TemporaryDirectory() as directory:
   c=self.make()
   h=c['characters'][0]
   town_services.accept(c,'Supply Run')
   before=(h['gold'],h['xp'])
   for _ in range(3):
    c['turn']+=1
   c['location']='market'
   with self.assertRaises(ValueError):town_services.complete(c)
   c['location']='square'
   with self.assertRaises(ValueError):town_services.complete(c)
   story.select(c,'market')
   self.assertTrue(c['guild_job']['visited_goal'])
   game.save(directory,c)
   c=game.load_all(directory)[0]
   story.select(c,'square')
   town_services.complete(c)
   self.assertIsNone(c['guild_job'])
   self.assertGreater(c['characters'][0]['gold'],before[0])
   with self.assertRaises(ValueError):town_services.complete(c)
 def test_content_update_rollback_preserves_campaign_bytes(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)
   campaign=self.make()
   game.save(root,campaign)
   savefile=root/'campaigns'/(campaign['id']+'.json')
   original=savefile.read_bytes()
   responses={}
   def build(version,body):
    location='stories/hollow-bell.json'
    url=addon_updates.ORIGIN+'/updates/'+version+'/'+location
    manifest={'version':version,'files':[{'path':location,'url':url,'sha256':hashlib.sha256(body).hexdigest()}]}
    responses[addon_updates.MANIFEST]=json.dumps(manifest).encode()
    responses[url]=body
   build('1.0.0',b'{"scene":"old"}')
   self.assertEqual(addon_updates.check_and_install(root,lambda url:responses[url])[0],'updated')
   build('1.0.1',b'{"scene":"new"}')
   self.assertEqual(addon_updates.check_and_install(root,lambda url:responses[url])[0],'updated')
   self.assertEqual(addon_updates.current(root),'1.0.1')
   update_addons.rollback(root)
   self.assertEqual(addon_updates.current(root),'1.0.0')
   self.assertEqual(savefile.read_bytes(),original)
   self.assertEqual(game.load_all(root)[0]['id'],campaign['id'])
if __name__=='__main__':unittest.main()
