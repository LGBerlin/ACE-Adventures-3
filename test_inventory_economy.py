import random,tempfile,unittest
from pathlib import Path
import game,story
class InventoryEconomyTests(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign('Economy',2)
  for name in ('Alpha','Beta'):game.add_hero(self.c,game.character(name,22,'Fighter',random.Random(len(name))))
  game.start(self.c)
 def test_buy_and_heal_and_save(self):
  c=self.c
  story.select(c,'market')
  h=c['characters'][0];h['gold']=12;h['hp']=h['max_hp']-10
  story.select(c,'buy_potion')
  self.assertEqual(h['gold'],3);self.assertIn('Healing Draught',h['inventory'])
  msg=game.use_item(c,'Healing Draught');self.assertIn('10 HP',msg)
  self.assertEqual(h['hp'],h['max_hp']);self.assertNotIn('Healing Draught',h['inventory'])
  with tempfile.TemporaryDirectory() as td:
   game.save(td,c);reloaded=game.load_all(td)[0]
   self.assertEqual(reloaded['characters'][0]['gold'],3)
   self.assertEqual(reloaded['characters'][0]['hp'],h['max_hp'])
 def test_no_free_gold_or_healing(self):
  c=self.c;story.select(c,'market');h=c['characters'][0];h['gold']=8
  with self.assertRaises(ValueError):story.select(c,'buy_potion')
  self.assertEqual(h['gold'],8)
  h['hp']=h['max_hp']-5
  with self.assertRaises(ValueError):game.use_item(c,'Healing Draught')
  self.assertEqual(h['hp'],h['max_hp']-5)
 def test_combat_potion_provokes_retaliation(self):
  c=self.c;h=c['characters'][0]
  h['inventory'].append('Healing Draught')
  h['hp']=h['max_hp']-10
  c['enemy']={'name':'Wolf','hp':12,'ac':12}
  class FixedRng:
   def randint(self,a,b):return 4
  before=c['turn']
  msg=game.use_item(c,'Healing Draught',rng=FixedRng())
  self.assertEqual(h['hp'],h['max_hp']-4)
  self.assertEqual(c['turn'],before+1)
  self.assertIn('retaliates for 4 HP',msg)
 def test_one_character_inventory_independent(self):
  c=self.c;a,b=c['characters'];a['hp']-=5;b['hp']-=5;a['inventory'].append('Healing Draught')
  c['active']=1
  with self.assertRaises(ValueError):game.use_item(c,'Healing Draught')
  self.assertEqual(b['hp'],b['max_hp']-5)
  game.use_item(c,'Healing Draught',0)
  self.assertEqual(a['hp'],a['max_hp']);self.assertEqual(b['hp'],b['max_hp']-5)
if __name__=='__main__':unittest.main()