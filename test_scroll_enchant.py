import random
import unittest
import game
import training_scrolls
import loot_system
class ScrollAndEnchantTests(unittest.TestCase):
 def make(self,kind):
  c=game.new_campaign("Scroll test",1)
  h=game.character("Arin",24,kind,random.Random(2))
  game.add_hero(c,h);game.start(c)
  game.award_experience(h,3000)
  return c,h
 def test_scrolls_for_every_class(self):
  for kind in game.PATHS:
   c,h=self.make(kind)
   if kind=="Mage":
    item="Scroll: "+h["magic"]+" Sigil"
   else:
    item="Scroll: "+h["path"]+" Secret Art"
   h["inventory"].append(item)
   self.assertNotIn(training_scrolls.SCROLLS[item]["ability"],h["moves"])
   training_scrolls.study(c,item)
   self.assertIn(training_scrolls.SCROLLS[item]["ability"],h["moves"])
   self.assertNotIn(item,h["inventory"])
 def test_scroll_cannot_bypass_level_requirement(self):
  c=game.new_campaign("Locked scroll",1)
  h=game.character("Arin",24,"Mage",random.Random(2))
  game.add_hero(c,h);game.start(c)
  item="Scroll: "+h["magic"]+" Sigil"
  h["inventory"].append(item)
  with self.assertRaises(ValueError):training_scrolls.study(c,item)
 def test_enchanted_armor_has_mechanical_bonus(self):
  c,h=self.make("Fighter")
  c["location"]="market"
  h["gold"]=100
  h["inventory"].append("Chainmail")
  loot_system.equip(c,"Chainmail")
  old=loot_system.bonuses(h)["defense"]
  class FrostSpin:
   def randrange(self,n):return 1
  loot_system.enchant(c,"Chainmail",FrostSpin())
  self.assertEqual(loot_system.bonuses(h)["defense"],old+1)
if __name__=="__main__":unittest.main()
