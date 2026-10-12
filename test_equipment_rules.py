import random,unittest
import game,shop
class EquipmentRulesTests(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign('Equipment',1)
  self.h=game.character('Bron',25,'Fighter',random.Random(5))
  game.add_hero(self.c,self.h);game.start(self.c)
 def test_starting_weapon_equipped(self):
  self.assertIn(self.h['equipment']['weapon'],self.h['inventory'])
 def test_equip_owned_bow_changes_slot_and_persists(self):
  self.h['inventory'].append('Short Bow')
  game.equip(self.c,'Short Bow')
  self.assertEqual(self.h['equipment']['weapon'],'Short Bow')
  self.assertIn('Short Bow',self.h['inventory'])
 def test_cannot_equip_unowned_or_food(self):
  with self.assertRaisesRegex(ValueError,'not own'):game.equip(self.c,'Leather Armor')
  with self.assertRaisesRegex(ValueError,'not equipable'):game.equip(self.c,'Travel Rations')
 def test_armor_reduces_damage_and_cannot_change_midfight(self):
  self.h['inventory'].append('Leather Armor')
  game.equip(self.c,'Leather Armor')
  before=self.h['hp']
  self.assertEqual(game._apply_incoming(self.h,3),2)
  self.assertEqual(self.h['hp'],before-2)
  self.c['enemy']={'name':'Wolf','hp':12,'ac':12}
  with self.assertRaisesRegex(ValueError,'combat'):game.equip(self.c,'Iron Sword')
 def test_market_sells_real_equipment(self):
  self.c['location']='market'
  self.h['gold']=30
  shop.buy(self.c,'Leather Armor')
  self.assertIn('Leather Armor',self.h['inventory'])
  game.equip(self.c,'Leather Armor')
  self.assertEqual(self.h['equipment']['armor'],'Leather Armor')
