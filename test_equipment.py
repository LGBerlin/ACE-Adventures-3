import random
import tempfile
import unittest
import equipment
import game
import merchant
class EquipmentTests(unittest.TestCase):
    def setUp(self):
        self.c=game.new_campaign("Equipment",1)
        game.add_hero(self.c,game.character("Aster",25,"Fighter",random.Random(3)))
        game.start(self.c)
        self.h=self.c["characters"][0]
    def test_equips_owned_class_legal_weapon_and_saves(self):
        equipment.equip(self.c,"Iron Sword")
        self.assertEqual(equipment.equipped(self.h),"Iron Sword")
        self.assertEqual(equipment.attack_bonus(self.h),1)
        with tempfile.TemporaryDirectory() as folder:
            game.save(folder,self.c)
            loaded=game.load_all(folder)[0]
            self.assertEqual(equipment.equipped(loaded["characters"][0]),"Iron Sword")
    def test_cannot_equip_unowned_or_invalid(self):
        with self.assertRaises(ValueError):equipment.equip(self.c,"Ashwood Staff")
        with self.assertRaises(ValueError):equipment.equip(self.c,"Health Potion")
    def test_sell_equipped_weapon_deactivates_bonus(self):
        equipment.equip(self.c,"Iron Sword")
        self.c["location"]="market"
        merchant.sell(self.c,"Iron Sword")
        self.assertIsNone(equipment.equipped(self.h))
        self.assertEqual(equipment.attack_bonus(self.h),0)
    def test_battle_blocks_switching_equipment(self):
        self.c["enemy"]={"name":"Wolf","hp":15,"ac":12}
        with self.assertRaises(ValueError):equipment.equip(self.c,"Iron Sword")
    def test_equipped_weapon_increases_attack_modifier(self):
        import interaction
        equipment.equip(self.c,"Iron Sword")
        game.encounter(self.c,random.Random(3))
        result=interaction.perform(self.c,"I attack the enemy",random.Random(1))
        baseline=(self.h["stats"]["STR"]-10)//2
        self.assertEqual(result["modifier"],baseline+1)
    def test_typed_equipment_never_rolls(self):
        import interaction
        result=interaction.perform(self.c,"equip Iron Sword")
        self.assertFalse(result["roll_required"])
        self.assertEqual(equipment.equipped(self.h),"Iron Sword")
        result=interaction.perform(self.c,"unequip")
        self.assertFalse(result["roll_required"])
        self.assertIsNone(equipment.equipped(self.h))
    def test_old_campaign_has_no_assumed_bonus(self):
        self.assertIsNone(equipment.equipped(self.h))
        self.assertEqual(equipment.attack_bonus(self.h),0)
if __name__=="__main__":unittest.main()
