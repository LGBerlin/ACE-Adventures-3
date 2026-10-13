"""Audit modern/legacy equipment, merchant sales and combat modifiers."""
import random
import unittest
import game
import equipment
import loot_system
import merchant

class EquipmentConvergence(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign('Gear audit',1)
  game.add_hero(self.c,game.character('Aster',24,'Fighter',random.Random(7)))
  game.start(self.c)
  self.h=self.c['characters'][0]
  self.h['inventory']+=['Greatsword','Chainmail']
  self.h['gold']=100
 def total_attack_bonus(self):
  return equipment.attack_bonus(self.h)+loot_system.bonuses(self.h)['attack']
 def test_modern_weapon_displaces_legacy(self):
  equipment.equip(self.c,'Iron Sword')
  self.assertEqual(self.total_attack_bonus(),1)
  loot_system.equip(self.c,'Greatsword')
  self.assertIsNone(equipment.equipped(self.h))
  self.assertEqual(self.total_attack_bonus(),3)
 def test_legacy_weapon_displaces_modern(self):
  loot_system.equip(self.c,'Greatsword')
  equipment.equip(self.c,'Iron Sword')
  self.assertEqual(self.total_attack_bonus(),1)
  self.assertNotIn('weapon',self.h.get('gear_slots',{}))
 def test_selling_last_equipped_enchanted_item_removes_effects(self):
  self.c['location']='market'
  loot_system.equip(self.c,'Chainmail')
  self.h['enchantments']={'Chainmail':2}
  self.h['enchant_types']={'Chainmail':'Frost'}
  self.assertEqual(loot_system.bonuses(self.h)['defense'],4)
  merchant.sell(self.c,'Chainmail')
  self.assertEqual(loot_system.bonuses(self.h)['defense'],0)
  self.assertNotIn('armor',self.h['gear_slots'])
  self.assertNotIn('Chainmail',self.h['enchantments'])
  merchant.buy(self.c,'Chainmail')
  self.assertEqual(loot_system.bonuses(self.h)['defense'],0)
 def test_sold_legacy_weapon_stops_modifiers(self):
  self.c['location']='market'
  equipment.equip(self.c,'Iron Sword')
  merchant.sell(self.c,'Iron Sword')
  self.assertIsNone(equipment.equipped(self.h))
  self.assertEqual(self.total_attack_bonus(),0)
if __name__=='__main__':unittest.main()
