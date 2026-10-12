"""Every starting spell and technique evolves between major unlock milestones."""
import random
import unittest
import game
import ability_progression as p
import visual_mapping

class EveryAbilityEvolves(unittest.TestCase):
 def hero(self,kind,subtype):
  h=game.character('Training Hero',25,kind,random.Random(3))
  if kind=='Mage':
   h['magic']=subtype
   h['moves']=list(game.SPELLS[subtype])
  else:
   h['path']=subtype
   h['moves']=list(game.MOVES[subtype])
  return h
 def test_all_four_classes_and_all_paths_have_trainable_basics(self):
  for cls,paths in game.PATHS.items():
   for subtype in (list(game.SPELLS) if cls=='Mage' else paths):
    h=self.hero(cls,subtype)
    for move in list(h['moves']):
     with self.subTest(cls=cls,subtype=subtype,move=move):
      self.assertEqual(p.rank(h,move),1)
      base=p.damage_bonus(h,move)
      h['level']=5
      self.assertGreater(p.rank(h,move),1)
      self.assertGreater(p.damage_bonus(h,move),base)
      self.assertIn('Refined',p.display_name(h,move))
      self.assertEqual(visual_mapping.evolution(h,'I use '+move)['tier'],2)
      h['level']=20
      self.assertIn('Empowered',p.display_name(h,move))
      self.assertEqual(visual_mapping.evolution(h,'I use '+move)['tier'],3)
      h['level']=60
      self.assertIn('Mythic',p.display_name(h,move))
      self.assertEqual(visual_mapping.evolution(h,'I use '+move)['tier'],4)
      h['level']=1
 def test_new_skills_keep_internal_name_and_unlock_requirements(self):
  h=self.hero('Mage','Fire')
  h['level']=5
  self.assertEqual(p.rank(h,'Inferno Ring'),0)
  self.assertEqual(p.display_name(h,'Inferno Ring'),'Inferno Ring')
  self.assertEqual(p.tier(h,'Inferno Ring'),1)
 def test_training_does_not_mutate_inventory_or_learn_unauthorized_move(self):
  h=self.hero('Fighter','Knight')
  old_inventory=list(h['inventory'])
  old_moves=list(h['moves'])
  h['level']=100
  p.damage_bonus(h,'Guard')
  p.display_name(h,'Guard')
  self.assertEqual(h['inventory'],old_inventory)
  self.assertEqual(h['moves'],old_moves)
if __name__=='__main__':unittest.main()
