import random
import unittest
import game
import merchant
import loot_system
import town_services
import interaction
class TownLootIntegrationTests(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign("Town and loot",1)
  game.add_hero(self.c,game.character("Aster",22,"Fighter",random.Random(2)))
  game.start(self.c)
 def test_purchase_equip_and_enchant(self):
  h=self.c["characters"][0];h["gold"]=200
  self.c["location"]="market"
  interaction.perform(self.c,"buy Chainmail")
  interaction.perform(self.c,"equip Chainmail")
  self.assertEqual(loot_system.bonuses(h)["defense"],2)
  interaction.perform(self.c,"enchant Chainmail")
  self.assertEqual(h["enchantments"]["Chainmail"],1)
  self.assertEqual(h["gold"],150)
 def test_class_restriction(self):
  h=self.c["characters"][0]
  h["inventory"].append("Mystic Robe")
  with self.assertRaises(ValueError):loot_system.equip(self.c,"Mystic Robe")
 def test_townsfolk_and_guild(self):
  self.assertIn("Nella",interaction.perform(self.c,"talk to Nella")["result"])
  interaction.perform(self.c,"accept guild job Supply Run")
  self.c["location"]="market"
  interaction.perform(self.c,"look around")
  result=interaction.perform(self.c,"claim guild reward")
  self.assertIn("completed",result["result"])
  self.assertIsNone(self.c["guild_job"])
 def test_no_reward_without_job(self):
  with self.assertRaises(ValueError):town_services.complete(self.c)
 def test_story_quest_npc_untouched(self):
  interaction.perform(self.c,"talk to Elder Sera")
  self.assertEqual(self.c["quest"]["stage"],1)
if __name__=="__main__":unittest.main()
