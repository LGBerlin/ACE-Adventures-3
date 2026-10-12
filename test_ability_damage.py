"""Verify learned offensive actions actually differ from basic strikes."""
import random
import unittest
import game

class AbilityDamageTests(unittest.TestCase):
 def make(self):
  hero=game.character("Aster",24,"Fighter",random.Random(4))
  c=game.new_campaign("Ability damage",1)
  game.add_hero(c,hero)
  game.start(c)
  c["enemy"]={"name":"Dummy","hp":100,"max_hp":100,"ac":12}
  return c,hero
 def test_known_strike_hits_harder_than_basic_attack(self):
  class Fixed:
   def randint(self,a,b):return b
  plain,hero=self.make()
  basic=game.action(plain,"I attack the enemy",Fixed())
  basic_damage=100-plain["enemy"]["hp"]
  special,hero=self.make()
  move=next(m for m in hero["moves"] if not any(k in m.lower() for k in ("guard","stance","parry","counter","ward")))
  result=game.action(special,"I use "+move,Fixed())
  self.assertIn("damage inflicted",result["result"])
  self.assertGreater(100-special["enemy"]["hp"],basic_damage)
 def test_special_ability_spends_mana(self):
  class Fixed:
   def randint(self,a,b):return b
  c,hero=self.make()
  move=next(m for m in hero["moves"] if not any(k in m.lower() for k in ("guard","stance","parry","counter","ward")))
  mana=hero["mana"]
  if mana<3:hero["mana"]=3;mana=3
  game.action(c,"I use "+move,Fixed())
  self.assertEqual(hero["mana"],mana-3)
if __name__=="__main__":unittest.main()
