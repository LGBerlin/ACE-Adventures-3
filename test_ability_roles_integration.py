"""Rules-driven spell and technique effects through the same free-text battle path."""
import random
import unittest
import game
import interaction
import ability_effects

class AbilityRoleTests(unittest.TestCase):
 class Certain:
  def randint(self,a,b):return b
 def character_battle(self,cls,school=None,path=None):
  c=game.new_campaign('Ability roles',1)
  h=game.character('Caster',24,cls,random.Random(3))
  if school:
   h['magic']=school
   h['moves']=list(game.SPELLS[school])
  if path:
   h['path']=path
   h['moves']=list(game.MOVES[path])
  game.add_hero(c,h)
  game.start(c)
  c['enemy']={'name':'Practice Guardian','hp':100,'max_hp':100,'ac':10}
  h['mana']=max(10,h['mana'])
  h['max_mana']=max(h['max_mana'],h['mana'])
  return c,h
 def test_all_four_classes_have_a_defined_role_for_all_starting_moves(self):
  for cls,paths in game.PATHS.items():
   c,h=self.character_battle(cls)
   for move in h['moves']:
    with self.subTest(cls=cls,move=move):
     self.assertIn(ability_effects.role(h,move),('damage','control','ward','heal','mana'))
 def test_all_magic_schools_have_classified_actions(self):
  for school in game.SPELLS:
   c,h=self.character_battle('Mage',school=school)
   for move in h['moves']:
    self.assertNotEqual(ability_effects.role(h,move),'basic')
 def test_control_spell_staggers_enemy_and_costs_mana(self):
  c,h=self.character_battle('Mage',school='Gravity')
  start=h['mana']
  result=interaction.perform(c,'I cast Gravitational Push',self.Certain())
  self.assertTrue(result['roll_required'])
  self.assertEqual(c['enemy']['hp']<100,True)
  self.assertEqual(h['mana'],start-3)
  self.assertIn('staggered',result['result'])
 def test_protective_ability_changes_incoming_damage(self):
  c,h=self.character_battle('Fighter',path='Knight')
  h['hp']=h['max_hp']
  before=h['hp']
  result=interaction.perform(c,'I use Guard',self.Certain())
  self.assertTrue(result['roll_required'])
  self.assertEqual(h['hp'],before-1)
  self.assertEqual(h.get('ward_charges'),0)
 def test_support_spell_heals_without_damaging_enemy(self):
  c,h=self.character_battle('Mage',school='Support')
  h['hp']=h['max_hp']-12
  before=c['enemy']['hp']
  result=interaction.perform(c,'I cast Healing Wave',self.Certain())
  self.assertIn('HP restored',result['result'])
  self.assertEqual(c['enemy']['hp'],before)
if __name__=='__main__':unittest.main()
