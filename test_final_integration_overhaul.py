"""Final Phase 1 integration gate: gameplay, quest authority, AI narration, persistence."""
import copy
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import game
import interaction
import story
import dungeon_master
import town_services
import merchant
import loot_system

class IntegrationOverhaul(unittest.TestCase):
 class Maximum:
  def randint(self,a,b):return b
 def make(self):
  c=game.new_campaign('Integration audit',2)
  game.add_hero(c,game.character('Aster',23,'Fighter',random.Random(2)))
  game.add_hero(c,game.character('Bryn',24,'Mage',random.Random(3)))
  game.start(c)
  return c
 def test_unrelated_defeat_cannot_advance_boss_quest(self):
  c=self.make()
  c['quest']={'stage':3,'completed':False}
  c['enemy']={'name':'Moss Goblin','hp':1,'max_hp':15,'ac':10}
  outcome=interaction.perform(c,'I attack the goblin',self.Maximum())
  self.assertTrue(outcome['roll_required'])
  self.assertIsNone(c['enemy'])
  self.assertEqual(c['quest']['stage'],3)
  self.assertEqual(c['location'],'square')
 def test_real_guardian_defeat_advances_exactly_once(self):
  c=self.make()
  c['quest']={'stage':3,'completed':False}
  c['location']='forest'
  c['enemy']={'name':'Hollow Guardian','hp':1,'max_hp':30,'ac':14,'boss':True}
  interaction.perform(c,'I attack the guardian',self.Maximum())
  self.assertEqual(c['quest']['stage'],4)
  self.assertEqual(c['location'],'square')
  self.assertFalse(c['quest']['completed'])
  interaction.perform(c,'talk to Elder Sera')
  self.assertTrue(c['quest']['completed'])
 def test_ai_prompt_is_complete_and_pure(self):
  c=self.make()
  c['guild_jobs_completed']=2
  town_services.accept(c,'Herbalist Consultation')
  c['location']='market'
  c['last_enchant_spin']={'item':'Chainmail','slot':1,'outcome':'Frost','level':1}
  c['loot_history']=[{'item':'Guardian Ring','turn':5,'boss':False}]
  baseline=copy.deepcopy(c)
  context=dungeon_master.prompt_context(c,{'roll':7,'degree':'Failure','result':'Missed'})
  self.assertEqual(c,baseline)
  self.assertEqual(len(context['active_quests']),2)
  self.assertEqual(context['last_enchantment']['outcome'],'Frost')
  self.assertEqual(context['last_loot'][0]['item'],'Guardian Ring')
  self.assertEqual(context['authoritative_outcome']['degree'],'Failure')
  reply=dungeon_master.narrate(c,{'result':'Failed'},request=lambda body:{'message':{'content':'The guardian remains standing.'}})
  self.assertIn('remains standing',reply)
  self.assertEqual(c,baseline)
 def test_legacy_story_combat_cannot_complete_wrong_boss(self):
  c=self.make()
  c['quest']={'stage':3,'completed':False}
  c['enemy']={'name':'Forest Wisp','hp':1,'max_hp':15,'ac':10}
  with patch.object(random.Random,'randint',lambda self,a,b:b):
   result=story.select(c,'attack')
  self.assertIn('damage',result)
  self.assertIsNone(c['enemy'])
  self.assertEqual(c['quest']['stage'],3)
  self.assertEqual(len(c['dice_history']),1)
 def test_legacy_guard_stays_on_enemy_turn(self):
  c=self.make()
  c['quest']={'stage':3,'completed':False}
  c['enemy']={'name':'Hollow Guardian','hp':20,'max_hp':30,'ac':14,'boss':True}
  before=c['turn']
  story.select(c,'guard')
  self.assertEqual(c['turn'],before+1)
  self.assertEqual(c['quest']['stage'],3)
  self.assertEqual(len(c.get('dice_history',[])),1)
 def test_invented_cast_does_not_spend_mana_or_roll(self):
  c=self.make()
  c['active']=1
  h=c['characters'][1]
  mana=h['mana']
  c['enemy']={'name':'Hollow Guardian','hp':30,'max_hp':30,'ac':14,'boss':True}
  with self.assertRaisesRegex(ValueError,'not learned'):
   interaction.perform(c,'I cast an invented thunderfire spell',self.Maximum())
  self.assertEqual(h['mana'],mana)
  self.assertEqual(c['turn'],0)
  self.assertFalse(c.get('dice_history'))
 def test_known_school_spell_remains_available(self):
  c=self.make()
  c['active']=1
  h=c['characters'][1]
  c['enemy']={'name':'Training dummy','hp':50,'max_hp':50,'ac':10}
  known=h['moves'][0]
  result=interaction.perform(c,'I cast '+known,self.Maximum())
  self.assertTrue(result['roll_required'])
  self.assertEqual(len(c['dice_history']),1)
 def test_enchant_equipment_and_dice_are_saved_together(self):
  c=self.make()
  h=c['characters'][0];h['gold']=100;h['inventory'].append('Chainmail')
  c['location']='market'
  interaction.perform(c,'equip Chainmail')
  class Wheel:
   def randrange(self,n):return 1
  loot_system.enchant(c,'Chainmail',Wheel())
  c['enemy']={'name':'Training Wolf','hp':30,'max_hp':30,'ac':11}
  result=interaction.perform(c,'I attack the wolf',random.Random(5))
  self.assertTrue(result['roll_required'])
  with tempfile.TemporaryDirectory() as folder:
   game.save(folder,c)
   loaded=game.load_all(folder)[0]
   self.assertEqual(loaded['characters'][0]['gear_slots']['armor'],'Chainmail')
   self.assertEqual(loaded['characters'][0]['enchant_types']['Chainmail'],'Frost')
   self.assertEqual(len(loaded['dice_history']),1)
if __name__=='__main__':unittest.main()
