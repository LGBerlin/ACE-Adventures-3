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
 def test_abandon_only_optional_quest_and_reaccept(self):
  import interaction
  c=self.make()
  town_services.accept(c,'Supply Run')
  self.assertEqual(len(town_services.active_quests(c)),2)
  outcome=interaction.perform(c,'abandon guild job')
  self.assertFalse(outcome['roll_required'])
  self.assertIsNone(c['guild_job'])
  self.assertEqual(len(town_services.active_quests(c)),1)
  town_services.accept(c,'Tavern Errand')
  self.assertEqual(len(town_services.active_quests(c)),2)
  with self.assertRaises(ValueError):town_services.accept(c,'Supply Run')
 def test_cannot_abandon_during_encounter(self):
  c=self.make()
  town_services.accept(c,'Supply Run')
  game.encounter(c)
  with self.assertRaises(ValueError):town_services.abandon(c)
  self.assertIsNotNone(c['guild_job'])
 def test_npc_objective_persists_and_cannot_be_skipped(self):
  import interaction
  with tempfile.TemporaryDirectory() as folder:
   c=self.make()
   town_services.accept(c,'Herbalist Consultation')
   self.assertEqual(len(town_services.quest_status(c)),2)
   self.assertIn('Travel to the market',interaction.perform(c,'quest status')['result'])
   self.assertFalse(interaction.perform(c,'quest status')['roll_required'])
   story.select(c,'market')
   self.assertIn('Speak with Yarrow',town_services.quest_status(c)[1]['objective'])
   story.select(c,'square')
   with self.assertRaises(ValueError):town_services.complete(c)
   story.select(c,'market')
   interaction.perform(c,'talk to Yarrow')
   self.assertTrue(c['guild_job']['spoke_to_target'])
   game.save(folder,c)
   c=game.load_all(folder)[0]
   story.select(c,'square')
   old=c['characters'][0]['gold']
   town_services.complete(c)
   self.assertGreater(c['characters'][0]['gold'],old)
   self.assertEqual(len(town_services.quest_status(c)),1)
 def test_different_npc_does_not_satisfy_assignment(self):
  c=self.make()
  town_services.accept(c,'Inn Rumors')
  story.select(c,'tavern')
  town_services.talk(c,'Mira')
  self.assertFalse(c['guild_job']['spoke_to_target'])
  town_services.talk(c,'Tomas')
  self.assertTrue(c['guild_job']['spoke_to_target'])
 def test_quest_and_enchanted_gear_survive_content_rollback(self):
  import loot_system
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder)
   c=self.make()
   h=c['characters'][0]
   h['inventory'].append('Chainmail')
   h['gold']=100
   c['location']='market'
   loot_system.equip(c,'Chainmail')
   c['location']='square'
   town_services.accept(c,'Herbalist Consultation')
   story.select(c,'market')
   town_services.talk(c,'Yarrow')
   loot_system.enchant(c,'Chainmail')
   game.save(root,c)
   saved_before=(dict(c['guild_job']),dict(h['gear_slots']),dict(h['enchant_types']),list(h['inventory']))
   payload=b'{"locations":{"market":"Another description"}}'
   url=addon_updates.ORIGIN+'/updates/1.1.0/stories/hollow-bell.json'
   manifest={'version':'1.1.0','files':[{'path':'stories/hollow-bell.json','url':url,'sha256':hashlib.sha256(payload).hexdigest()}]}
   response={addon_updates.MANIFEST:json.dumps(manifest).encode(),url:payload}
   self.assertEqual(addon_updates.check_and_install(root,lambda key:response[key])[0],'updated')
   update_addons.rollback(root)
   loaded=game.load_all(root)[0]
   actual=loaded['characters'][0]
   self.assertEqual((loaded['guild_job'],actual['gear_slots'],actual['enchant_types'],actual['inventory']),saved_before)
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
