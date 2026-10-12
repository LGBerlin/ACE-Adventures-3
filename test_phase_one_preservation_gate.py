"""Phase 1 preservation gate before the later comprehensive integration audit.

These are structural contracts only; the final audit will additionally exercise
all transitions with the AI Dungeon Master and the illustrated macOS interface.
"""
import random
import unittest
import game
import spell_catalog
import technique_catalog
import merchant
import loot_system
import town_services
import interaction
import dice_ledger

class FeaturePreservationGate(unittest.TestCase):
 def test_four_classes_all_paths_and_schools_remain_available(self):
  self.assertEqual(set(game.PATHS),{'Fighter','Rogue','Mage','Vessel'})
  self.assertEqual(sum(map(len,game.PATHS.values())),17)
  self.assertEqual(len(game.SPELLS),14)
  self.assertTrue(technique_catalog.validate())
  self.assertEqual(set(spell_catalog.REGULAR),set(game.SPELLS))
  self.assertEqual(set(technique_catalog.REGULAR) if hasattr(technique_catalog,'REGULAR') else set(technique_catalog.TECHNIQUES),set(technique_catalog.TECHNIQUES))
 def test_merchant_equipment_guild_and_enchant_contract(self):
  self.assertTrue(set(loot_system.ITEMS).issubset(merchant.CATALOG))
  self.assertGreaterEqual(len(loot_system.ENCHANT_TYPES),6)
  self.assertGreaterEqual(len(town_services.JOBS),6)
  self.assertTrue(set(loot_system.ITEMS[k]['kind'] for k in loot_system.ITEMS)>={'weapon','armor','trinket'})
 def test_all_classes_have_starting_gear_and_abilities(self):
  for cls in game.PATHS:
   with self.subTest(cls=cls):
    hero=game.character('Tester',23,cls,random.Random(8))
    self.assertTrue(hero['inventory'])
    self.assertGreaterEqual(len(hero['moves']),3)
    self.assertEqual(hero['level'],1)
    self.assertEqual(hero['max_hp'],hero['hp'])
 def test_dice_only_for_uncertain_actions(self):
  c=game.new_campaign('Dice routing',1)
  game.add_hero(c,game.character('Tester',23,'Fighter',random.Random(4)))
  game.start(c)
  for command in ['look around','show quests','check my inventory']:
   response=interaction.perform(c,command)
   self.assertFalse(response['roll_required'])
  self.assertFalse(c.get('dice_history'))
  game.encounter(c,random.Random(3))
  response=interaction.perform(c,'I attack the enemy',random.Random(2))
  self.assertTrue(response['roll_required'])
  self.assertTrue(c.get('dice_history'))
if __name__=='__main__':unittest.main()
