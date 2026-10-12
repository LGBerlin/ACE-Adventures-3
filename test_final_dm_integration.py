"""Final AI DM integration contract over the complete authoritative game state."""
import copy
import json
import random
import unittest
import dungeon_master as dm
import game
import loot_system
import town_services

class AiIntegrationAudit(unittest.TestCase):
 def campaign(self):
  c=game.new_campaign('The Hollow Bell - audit',2)
  game.add_hero(c,game.character('Knight',23,'Fighter',random.Random(1)))
  game.add_hero(c,game.character('Mage',23,'Mage',random.Random(2)))
  game.start(c)
  return c
 def test_all_npc_and_quest_context_is_visible_without_mutation(self):
  c=self.campaign()
  town_services.accept(c,'Herbalist Consultation')
  c['location']='market'
  c['town_memory']={'Yarrow':3}
  c['enemy']={'name':'Hollow Guardian','hp':12,'max_hp':30,'ac':14,'boss':True,'phase':2}
  c['last_enchant_spin']={'item':'Chainmail','slot':1,'outcome':'Frost','level':1}
  c['loot_history']=[{'item':'Guardian Ring','turn':4,'boss':False}]
  knight=c['characters'][0]
  knight['inventory'].append('Chainmail')
  knight['gear_slots']={'armor':'Chainmail'}
  knight['enchantments']={'Chainmail':1}
  knight['enchant_types']={'Chainmail':'Frost'}
  before=copy.deepcopy(c)
  outcome={'roll':3,'degree':'Failure','result':'The guardian blocks the blow.'}
  context=dm.prompt_context(c,outcome)
  self.assertEqual(before,c)
  self.assertEqual(context['enemy']['phase'],2)
  self.assertEqual(context['last_loot'][0]['item'],'Guardian Ring')
  self.assertEqual(context['last_enchantment']['outcome'],'Frost')
  self.assertEqual(context['guild_rank'],'Novice')
  self.assertEqual(context['townsfolk']['Yarrow']['familiarity'],3)
  self.assertEqual(context['party'][0]['equipment_effects']['defense'],3)
  self.assertEqual(len(context['active_quests']),2)
  self.assertEqual(context['authoritative_outcome'],outcome)
 def test_model_cannot_grant_rewards_or_finish_quests(self):
  c=self.campaign()
  c['quest']={'stage':3,'completed':False}
  before=copy.deepcopy(c)
  def malicious_narration(body):
   self.assertIn('authoritative_outcome',body['messages'][-1]['content'])
   return {'message':{'content':'You instantly gain 10000 gold and the quest is completed.'}}
  prose=dm.narrate(c,{'result':'The attempt failed.'},request=malicious_narration)
  self.assertEqual(prose,'The attempt failed.')
  self.assertEqual(c,before)
 def test_unearned_boss_victory_is_not_narrated_as_fact(self):
  c=self.campaign()
  c['enemy']={'name':'Hollow Guardian','hp':30,'max_hp':30,'ac':14,'boss':True}
  prose=dm.narrate(c,{'result':'The guardian remains standing.'},request=lambda body:{'message':{'content':'The guardian is defeated!'}})
  self.assertEqual(prose,'The guardian remains standing.')
  self.assertEqual(c['enemy']['hp'],30)
 def test_legitimate_narration_is_preserved(self):
  c=self.campaign()
  prose=dm.narrate(c,'The market grows quiet.',request=lambda body:{'message':{'content':'The lanterns tremble in the breeze.'}})
  self.assertEqual(prose,'The lanterns tremble in the breeze.')
 def test_model_intents_cannot_edit_campaign(self):
  c=self.campaign()
  before=copy.deepcopy(c)
  for command in ('I go to the tavern','I cast Flame Flick','I attack the enemy','I buy armor'):
   action=dm.interpret(command,request=lambda body:{'message':{'content':json.dumps({'kind':'travel','target':'square','hp':99999,'gold':99999})}})
   self.assertEqual(set(action),{'kind','target','method'})
  self.assertEqual(c,before)
 def test_every_magic_school_is_safe_for_prompt_serialization(self):
  for school in game.SPELLS:
   c=game.new_campaign(school,1)
   h=game.character('Mage',24,'Mage',random.Random(3))
   h['magic']=school
   h['moves']=list(game.SPELLS[school])
   game.add_hero(c,h);game.start(c)
   context=dm.prompt_context(c,'Look at the scene.')
   json.dumps(context)
   self.assertEqual(context['party'][0]['known_abilities'],h['moves'])
if __name__=='__main__':unittest.main()
