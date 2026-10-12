import random,unittest
import game
class CombatTurns(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign('Combat',1)
  game.add_hero(self.c,game.character('Tester',25,'Fighter',random.Random(45)))
  game.start(self.c);game.encounter(self.c,random.Random(10))
 def test_negotiation_does_not_freeze_enemy(self):
  hero=self.c['characters'][0];hero['hp']=20
  class Dice:
   def randint(self,a,b):return b
  result=game.action(self.c,'I negotiate with the guardian',Dice())
  self.assertEqual(hero['hp'],16)
  self.assertIn('retaliates',result['result'])
 def test_guard_can_reduce_damage(self):
  hero=self.c['characters'][0];hero['hp']=20
  class Dice:
   def randint(self,a,b):return b
  game.action(self.c,'I guard and defend myself',Dice())
  self.assertEqual(hero['hp'],18)
  self.assertEqual(self.c['turn'],1)
if __name__=='__main__':unittest.main()