import unittest
from animation_director import Director

class AnimationDirectorTests(unittest.TestCase):
 def test_result_does_not_change_game(self):
  c={'name':'Ada','hp':15,'mana':8}
  result={'action':'I cast a flame spell','degree':'Success','result':'D20 success'}
  before=(c.copy(),result.copy())
  q=Director();cue=q.resolve_action(c,result)
  self.assertEqual(c,before[0]);self.assertEqual(result,before[1])
  self.assertEqual(cue.action,'cast')
 def test_invalid_animation_uses_idle(self):
  self.assertEqual(Director().enqueue('hero','/tmp/evil.py').action,'idle')
 def test_queue_and_effect_limits(self):
  q=Director(max_events=3,max_effects=1)
  q.enqueue('a','cast','fire')
  q.enqueue('b','cast','ice')
  self.assertEqual(q.events[-1].effect,'')
  q.enqueue('c','attack');q.enqueue('d','attack')
  self.assertEqual(len(q.events),3)
  self.assertEqual(len(q.drain(2)),2)
 def test_no_idle_loop(self):
  q=Director();self.assertEqual(q.drain(),[])
