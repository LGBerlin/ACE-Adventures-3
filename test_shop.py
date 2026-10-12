import random,unittest
import game,shop
class ShopBehaviorTests(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign('Test',1)
  game.add_hero(self.c,game.character('Merchant',21,'Rogue',random.Random(4)))
  game.start(self.c)
  self.c['characters'][0]['gold']=20
 def test_buy_item_updates_gold_inventory_and_story(self):
  self.c['location']='market'
  item='Healing Draught'
  response=shop.buy(self.c,item)
  self.assertIn(item,response)
  self.assertEqual(self.c['characters'][0]['gold'],11)
  self.assertIn(item,self.c['characters'][0]['inventory'])
  self.assertEqual(self.c['turn'],1)
 def test_no_remote_shopping(self):
  with self.assertRaises(ValueError):shop.buy(self.c,'Torch')
 def test_insufficient_gold_atomic(self):
  self.c['location']='market'
  self.c['characters'][0]['gold']=1
  before=(list(self.c['characters'][0]['inventory']),self.c['turn'])
  with self.assertRaisesRegex(ValueError,'Not enough gold'):shop.buy(self.c,'Torch')
  self.assertEqual(before,(self.c['characters'][0]['inventory'],self.c['turn']))
 def test_no_shopping_in_combat(self):
  self.c['location']='market'
  self.c['enemy']={'name':'Guardian','hp':5,'ac':10}
  with self.assertRaises(ValueError):shop.buy(self.c,'Torch')
 def test_unknown_items_rejected(self):
  self.c['location']='market'
  with self.assertRaises(ValueError):shop.buy(self.c,'Legendary Sword')
