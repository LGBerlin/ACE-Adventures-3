import random
import unittest
import game
import story
import town_services
import loot_system
import merchant
class PhaseOneQuestBattleTests(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign("Quests and loot",1)
  game.add_hero(self.c,game.character("Arin",22,"Fighter",random.Random(2)))
  game.start(self.c)
 def test_two_quest_limit(self):
  self.assertEqual(len(town_services.active_quests(self.c)),1)
  town_services.accept(self.c,"Supply Run")
  self.assertEqual(len(town_services.active_quests(self.c)),2)
  with self.assertRaises(ValueError):town_services.accept(self.c,"Tavern Errand")
 def test_enchant_spin_persists_and_charges(self):
  h=self.c["characters"][0];h["inventory"].append("Chainmail");h["gold"]=70
  self.c["location"]="market"
  class Fixed:
   def randrange(self,n):return 2
  loot_system.enchant(self.c,"Chainmail",Fixed())
  self.assertEqual(self.c["last_enchant_spin"]["outcome"],"Storm")
  self.assertEqual(h["gold"],55)
  self.assertEqual(h["enchant_types"]["Chainmail"],"Storm")
 def test_guardian_is_boss_and_drops_loot(self):
  self.c["quest"]={"stage":3,"completed":False}
  game.encounter(self.c,random.Random(3))
  self.assertTrue(self.c["enemy"]["boss"])
  self.assertEqual(self.c["enemy"]["name"],"Hollow Guardian")
  self.c["enemy"]["hp"]=1
  class High:
   def randint(self,a,b):return b
  hero=self.c["characters"][0]
  game.action(self.c,"I attack",High())
  self.assertIsNone(self.c["enemy"])
  self.assertIn("Hollow Guardian Relic",hero["inventory"])
  self.assertTrue(self.c["loot_history"][-1]["boss"])
 def test_boss_relic_can_be_sold_but_not_purchased(self):
  self.c["location"]="market"
  h=self.c["characters"][0]
  with self.assertRaises(ValueError):merchant.buy(self.c,"Hollow Guardian Relic")
  h["inventory"].append("Hollow Guardian Relic")
  gold=h["gold"]
  merchant.sell(self.c,"Hollow Guardian Relic")
  self.assertEqual(h["gold"],gold+40)
 def test_loot_can_be_sold(self):
  self.c["quest"]={"stage":3,"completed":False}
  game.encounter(self.c,random.Random(3))
  self.c["enemy"]["hp"]=1
  class High:
   def randint(self,a,b):return b
  game.action(self.c,"I attack",High())
  self.c["location"]="market"
  hero=self.c["characters"][0]
  before=hero["gold"]
  merchant.sell(self.c,"Guardian Ring")
  self.assertGreater(hero["gold"],before)
if __name__=="__main__":unittest.main()
