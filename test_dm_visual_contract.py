import unittest,random
import game,visual_mapping
from animation_director import Director

class DmToVisualContractTests(unittest.TestCase):
 def test_verified_game_action_creates_visual_cue(self):
  c=game.new_campaign('Link',1)
  hero=game.character('Ada',25,'Fighter',random.Random(3))
  game.add_hero(c,hero);game.start(c);game.encounter(c,random.Random(1))
  director=Director()
  result=game.action(c,'I strike the enemy',random.Random(5))
  visual=visual_mapping.cue_for(hero,result)
  cue=director.enqueue(hero['id'],visual['animation'],visual['effect'] or '')
  self.assertEqual(cue.action,'attack')
  self.assertGreater(c['turn'],0)
  self.assertTrue(cue.duration_ms<=1200)
 def test_effect_selection_cannot_change_authoritative_dice(self):
  c=game.new_campaign('Link',1)
  hero=game.character('Ava',23,'Mage',random.Random(4))
  game.add_hero(c,hero);game.start(c);game.encounter(c,random.Random(1))
  result=game.action(c,'I cast a spell',random.Random(9))
  before=(result.copy(),hero['hp'],hero['mana'],c['turn'])
  visual_mapping.cue_for(hero,result)
  self.assertEqual(before,(result,hero['hp'],hero['mana'],c['turn']))
