import random
import unittest
import game
class SupportSpellEffects(unittest.TestCase):
 def setUp(self):
  self.hero=game.character("Iris",23,"Mage",random.Random(4))
  self.hero["magic"]="Support"
  self.hero["moves"]=list(game.SPELLS["Support"])
  self.c=game.new_campaign("Support rules",1)
  game.add_hero(self.c,self.hero)
  game.start(self.c)
  class Certain:
   def randint(self,a,b):return b
  self.good=Certain()
 def test_healing_wave_changes_health_not_gold(self):
  h=self.hero;h["hp"]=h["max_hp"]-12
  before=h["gold"]
  result=game.action(self.c,"I cast Healing Wave",self.good)
  self.assertGreater(h["hp"],h["max_hp"]-12)
  self.assertEqual(h["gold"],before)
  self.assertIn("HP restored",result["result"])
 def test_mana_boost_changes_mana_with_cost(self):
  h=self.hero;h["mana"]=5
  game.action(self.c,"I cast Mana Boost",self.good)
  self.assertGreater(h["mana"],2)
  self.assertLessEqual(h["mana"],h["max_mana"])
 def test_healing_in_battle_allows_retaliation(self):
  h=self.hero;h["hp"]=h["max_hp"]-10
  self.c["enemy"]={"name":"Wolf","hp":15,"ac":12}
  result=game.action(self.c,"I cast Healing Wave",self.good)
  self.assertIn("retaliates",result["result"])
  self.assertEqual(self.c["enemy"]["hp"],15)
if __name__=="__main__":unittest.main()
