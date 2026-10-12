import unittest
from story_tree import timeline,journal_text
class StoryTreeTests(unittest.TestCase):
 def test_initial_and_finished(self):
  c={'quest':{'stage':0,'completed':False}}
  self.assertEqual(timeline(c)[0]['status'],'completed')
  self.assertEqual(timeline(c)[1]['status'],'current')
  c['quest']={'stage':4,'completed':True}
  self.assertTrue(all(x['status']=='completed' for x in timeline(c)))
 def test_no_mutation(self):
  c={'quest':{'stage':2,'completed':False}}
  before={'quest':dict(c['quest'])}
  self.assertIn('Traced the carvings',journal_text(c))
  self.assertEqual(c,before)
