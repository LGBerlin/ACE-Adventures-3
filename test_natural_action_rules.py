import random,unittest
import game,interaction,story
class NaturalInputTests(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign('Natural',1)
  game.add_hero(self.c,game.character('Nora',22,'Rogue',random.Random(4)))
  game.start(self.c)
  story.ensure(self.c)
 def test_harmless_actions_do_not_roll(self):
  for action in ('I listen to the rain','I examine the square','I wait','I look around'):
   before=self.c['turn']
   result=interaction.perform(self.c,action)
   self.assertFalse(result['roll_required'],action)
   self.assertEqual(self.c['turn'],before+1)
 def test_ordinary_market_travel_not_rolled(self):
  result=interaction.perform(self.c,'I want to go to the market')
  self.assertFalse(result['roll_required'])
  self.assertEqual(self.c['location'],'market')
 def test_risky_action_still_rolls(self):
  result=interaction.perform(self.c,'I sneak through the shadows',random.Random(3))
  self.assertTrue(result['roll_required'])
 def test_no_arbitrary_combat_with_absent_enemy(self):
  with self.assertRaisesRegex(ValueError,'no opponent'):
   interaction.perform(self.c,'I attack a wolf')
 def test_bad_model_intent_cannot_grant_outcome(self):
  result=interaction.perform(self.c,'I look around',intent={'kind':'other','gold':1000,'quest':'complete'})
  self.assertFalse(result['roll_required'])
  self.assertNotIn('gold',result)
