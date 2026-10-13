import random
import unittest
import game
import loot_system
import interaction
class ManaGearIntegration(unittest.TestCase):
 class Fixed:
  def randint(self,a,b):return b
 def test_equipped_mana_gear_reduces_cost_but_not_to_zero(self):
  c=game.new_campaign('Mana equipment',1)
  h=game.character('Iris',25,'Mage',random.Random(4))
  h['magic']='Fire';h['moves']=list(game.SPELLS['Fire'])
  game.add_hero(c,h);game.start(c)
  h['inventory'].append('Sage Amulet')
  h['inventory'].append('Mystic Robe')
  h['mana']=10;h['max_mana']=max(h['max_mana'],10)
  loot_system.equip(c,'Sage Amulet')
  loot_system.equip(c,'Mystic Robe')
  c['enemy']={'name':'Practice target','hp':100,'max_hp':100,'ac':10}
  result=interaction.perform(c,'I cast Flame Flick',self.Fixed())
  self.assertTrue(result['roll_required'])
  self.assertEqual(h['mana'],9)
 def test_unequipped_gear_does_not_grant_discount(self):
  c=game.new_campaign('No equipment',1)
  h=game.character('Iris',25,'Mage',random.Random(4))
  h['magic']='Fire';h['moves']=list(game.SPELLS['Fire'])
  game.add_hero(c,h);game.start(c)
  h['inventory'].append('Sage Amulet')
  h['mana']=10;h['max_mana']=max(h['max_mana'],10)
  c['enemy']={'name':'Practice target','hp':100,'max_hp':100,'ac':10}
  interaction.perform(c,'I cast Flame Flick',self.Fixed())
  self.assertEqual(h['mana'],7)
if __name__=='__main__':unittest.main()
