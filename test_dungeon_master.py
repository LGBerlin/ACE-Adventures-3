import copy,random,unittest
import game,dungeon_master as dm
class DungeonMasterTests(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign('Story',1);game.add_hero(self.c,game.character('Alice',25,'Fighter',random.Random(9)));game.start(self.c)
 def test_npc_memory_survives_save(self):
  dm.remember(self.c,'sera','I ask about the bell','She answers cautiously.')
  self.assertEqual(dm.ensure_world(self.c)['npc_memory']['sera'][0]['player'],'I ask about the bell')
  self.assertIn('I ask about the bell',str(dm.prompt_context(self.c,'Sera replied')))
  with self.assertRaises(ValueError):dm.remember(self.c,'mira','hi','hello')
 def test_model_cannot_mutate_state(self):
  before=copy.deepcopy(self.c)
  result=dm.interpret('I convince the guard to let us pass',request=lambda b:{'message':{'content':'{"kind":"speak","hp":999,"gold":100000,"quest":"complete"}'}})
  self.assertEqual(result['kind'],'speak')
  self.assertNotIn('gold',result);self.assertEqual(self.c,before)
 def test_offline_interpreter(self):
  a=dm.interpret('I inspect the strange runes on the well',request=lambda b: (_ for _ in ()).throw(OSError('offline')))
  self.assertEqual(a['kind'],'investigate')
 def test_narrator_receives_fact_checks(self):
  def mock(b):
   self.assertIn('authoritative_outcome',b['messages'][-1]['content'])
   self.assertIn('failed',b['messages'][-1]['content'])
   return {'message':{'content':'The gate remains shut. A guard raises an eyebrow.'}}
  before=copy.deepcopy(self.c)
  self.assertIn('gate remains shut',dm.narrate(self.c,'The attempt failed.',request=mock))
  self.assertEqual(self.c,before)
 def test_clues_are_idempotent(self):
  dm.discover(self.c,'A bootprint');dm.discover(self.c,'A bootprint')
  self.assertEqual(dm.ensure_world(self.c)['clues'],['A bootprint'])
if __name__=='__main__':unittest.main()