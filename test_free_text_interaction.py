import unittest,random
import game,interaction,story
class FreeTextInteractionTests(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign('Test',1)
  game.add_hero(self.c,game.character('A',20,'Rogue',random.Random(1)))
  game.start(self.c);story.ensure(self.c)
 def test_market_travel_requires_no_roll(self):
  result=interaction.perform(self.c,'I want to go to the market')
  self.assertFalse(result['roll_required'])
  self.assertEqual(self.c['location'],'market')
 def test_regular_npc_conversation_without_roll(self):
  interaction.perform(self.c,'go to market')
  result=interaction.perform(self.c,'I want to ask Yarrow about the ruins')
  self.assertFalse(result['roll_required'])
 def test_progression_gates_still_apply(self):
  with self.assertRaises(ValueError):interaction.perform(self.c,'go to forest')
  self.assertEqual(self.c['location'],'square')
 def test_uncertain_attack_still_uses_dice(self):
  self.c['enemy']={'name':'Wolf','hp':15,'ac':12}
  result=interaction.perform(self.c,'I attack the wolf',random.Random(1))
  self.assertTrue(result['roll_required'])
  self.assertIn('roll',result)
 def test_nonroll_action_does_not_change_xp(self):
  before=self.c['characters'][0]['xp']
  response=interaction.perform(self.c,'look around')
  self.assertFalse(response['roll_required'])
  self.assertEqual(self.c['characters'][0]['xp'],before)
