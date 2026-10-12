"""Replayable guild and persistent townsfolk integration."""
import random
import tempfile
import unittest
import game
import story
import merchant
import town_services
import interaction

class ReplayableTownTests(unittest.TestCase):
 def make(self):
  c=game.new_campaign('Briarhollow work',1)
  game.add_hero(c,game.character('Rowan',24,'Fighter',random.Random(2)))
  game.start(c)
  return c
 def test_delivery_requires_quest_trip_item_and_return(self):
  c=self.make()
  hero=c['characters'][0]
  hero['gold']=25
  town_services.accept(c,'Medicine Delivery')
  story.select(c,'market')
  self.assertIn('Obtain Healing Draught',town_services.quest_status(c)[1]['objective'])
  story.select(c,'square')
  with self.assertRaises(ValueError):
   town_services.complete(c)
  story.select(c,'market')
  merchant.buy(c,'Healing Draught')
  story.select(c,'square')
  before=(hero['gold'],hero['xp'])
  town_services.complete(c)
  self.assertNotIn('Healing Draught',hero['inventory'])
  self.assertEqual(hero['gold'],before[0]+16)
  self.assertEqual(c['guild_jobs_completed'],1)
  with self.assertRaises(ValueError):
   town_services.complete(c)
 def test_npc_familiarity_persists_and_does_not_require_dice(self):
  c=self.make()
  first=interaction.perform(c,'talk to Nella')
  second=interaction.perform(c,'talk to Nella')
  self.assertFalse(first['roll_required'])
  self.assertFalse(second['roll_required'])
  self.assertIn('Welcome back',second['result'])
  with tempfile.TemporaryDirectory() as folder:
   game.save(folder,c)
   restored=game.load_all(folder)[0]
   self.assertEqual(restored['town_memory']['Nella'],2)
   final=interaction.perform(restored,'talk to Nella')
   self.assertIn('familiar face',final['result'])
 def test_guild_rank_restricts_and_unlocks_higher_jobs(self):
  c=self.make()
  self.assertEqual(town_services.guild_rank(c),'Novice')
  with self.assertRaisesRegex(ValueError,'reputation'):
   town_services.accept(c,'Armory Requisition')
  self.assertNotIn('Armory Requisition',town_services.available_jobs(c))
  c['guild_jobs_completed']=2
  self.assertEqual(town_services.guild_rank(c),'Trusted')
  self.assertIn('Armory Requisition',town_services.available_jobs(c))
  town_services.accept(c,'Armory Requisition')
  with self.assertRaises(ValueError):town_services.accept(c,'Supply Run')
  town_services.abandon(c)
  c['guild_jobs_completed']=4
  self.assertEqual(town_services.guild_rank(c),'Veteran')
  self.assertIn('Veteran Reconnaissance',town_services.available_jobs(c))
 def test_defeated_or_remote_player_cannot_claim(self):
  c=self.make()
  town_services.accept(c,'Medicine Delivery')
  with self.assertRaises(ValueError):town_services.complete(c)
  c['enemy']={'name':'Wolf','hp':4,'ac':10}
  with self.assertRaises(ValueError):town_services.talk(c,'Nella')
if __name__=='__main__':unittest.main()
