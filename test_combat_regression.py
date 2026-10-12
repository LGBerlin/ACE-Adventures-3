import random,unittest
import game

class CombatRegressionTests(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign('Guard test',1)
  game.add_hero(self.c,game.character('Hero',24,'Fighter',random.Random(4)))
  game.start(self.c)
  game.encounter(self.c,random.Random(10))
 def test_guard_advances_turn_without_defeating_enemy(self):
  before=self.c['enemy']['hp']
  result=game.action(self.c,'I guard against the enemy attack',random.Random(3))
  self.assertEqual(self.c['turn'],1)
  self.assertEqual(self.c['enemy']['hp'],before)
  self.assertIn('Guard stance',result['result'])
 def test_guard_does_not_heal(self):
  self.c['characters'][0]['hp']=9
  game.action(self.c,'I defend and block',random.Random(1))
  self.assertLessEqual(self.c['characters'][0]['hp'],9)
 def test_defensive_actions_cannot_complete_quest(self):
  for seed in range(10):
   game.action(self.c,'I guard',random.Random(seed))
  self.assertIsNotNone(self.c['enemy'])
  self.assertEqual(self.c['enemy']['hp'],15)
