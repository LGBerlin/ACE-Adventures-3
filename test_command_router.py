"""Router regression tests: fixed UI, no fabricated spellcasting or combat escape."""
import unittest
import command_router

class CommandRouterTests(unittest.TestCase):
    def setUp(self):
        self.c={'enemy':None,'active':0,'characters':[{'moves':['Flame Flick']}]}

    def test_fixed_screens(self):
        for text,panel in (
            ('open inventory','Pack'),
            ('show character sheet','Record'),
            ('show my spells','Abilities'),
            ('open shop','Shop'),
            ('show world map','Map'),
            ('open dice board','Dice Board'),
            ('show quest journal','Journal')):
            with self.subTest(text=text):
                self.assertEqual(command_router.route(text,self.c),{'kind':'panel','panel':panel})

    def test_free_text_is_engine_action(self):
        self.assertEqual(command_router.route('walk to the tavern',self.c)['kind'],'action')
        self.assertEqual(command_router.route('attack the goblin',self.c)['text'],'attack the goblin')

    def test_unlearned_fireball_rejected(self):
        with self.assertRaisesRegex(ValueError,'not learned'):
            command_router.route('cast fireball at the goblin',self.c)

    def test_learned_fireball_dispatches_rules_action(self):
        self.c['characters'][0]['moves'].append('Fireball')
        self.assertEqual(command_router.route('cast fireball at the goblin',self.c)['text'],'cast fireball at the goblin')

    def test_learned_named_ability_preserves_target(self):
        self.c['characters'][0]['moves'].append('Ice Shard')
        self.assertEqual(command_router.route('cast Ice Shard at the skeleton',self.c)['text'],
                         'cast Ice Shard at the skeleton')

    def test_no_shop_during_combat(self):
        self.c['enemy']={'name':'Goblin'}
        for text in ('open shop','show world map','open town menu'):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError,'Finish the encounter'):
                command_router.route(text,self.c)

if __name__=='__main__':
    unittest.main()
