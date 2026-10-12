"""Integrated encounter: defenses, items, bosses and defeat."""
import random
import unittest
import game
import loot_system

class EncounterIntegrationTests(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign("Encounters",1)
  game.add_hero(self.c,game.character("Aster",25,"Fighter",random.Random(2)))
  game.start(self.c)
  self.h=self.c["characters"][0]
  game.encounter(self.c,random.Random(1))
 class MaxRoll:
  def randint(self,a,b):return b
 def test_armor_applies_to_retaliation_after_attack(self):
  self.h["inventory"].append("Chainmail")
  loot_system.equip(self.c,"Chainmail") if not self.c.get("enemy") else None
  self.h["gear_slots"]={"armor":"Chainmail"}
  before=self.h["hp"]
  game.action(self.c,"I attack the enemy",self.MaxRoll())
  self.assertGreaterEqual(self.h["hp"],before-2)
 def test_guard_and_potion_consistent_with_armor(self):
  self.h["inventory"].append("Chainmail")
  self.h["gear_slots"]={"armor":"Chainmail"}
  self.h["hp"]=self.h["max_hp"]-10
  self.h["inventory"].append("Health Potion")
  result=game.use_item(self.c,"Health Potion",rng=self.MaxRoll())
  self.assertIn("restores",result)
  self.assertEqual(self.h["hp"],self.h["max_hp"]-4)
 def test_party_defeat_persisted(self):
  self.h["hp"]=1
  game.action(self.c,"I negotiate",self.MaxRoll())
  self.assertTrue(self.c["party_defeated"])
 def test_boss_phase_used_for_potion_reaction(self):
  self.c["enemy"]={"name":"Hollow Guardian","hp":10,"max_hp":30,"ac":14,"boss":True}
  self.h["hp"]=self.h["max_hp"]-10
  self.h["inventory"].append("Healing Draught")
  message=game.use_item(self.c,"Healing Draught",rng=self.MaxRoll())
  self.assertIn("Bellshock",message)
  self.assertEqual(self.c["enemy"]["phase"],2)
if __name__=="__main__":unittest.main()
