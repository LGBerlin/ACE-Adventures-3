"""Release checks for idle CPU use and opt-in updates."""
import ast
from pathlib import Path
import unittest

class IdlePerformanceTests(unittest.TestCase):
    def test_no_network_update_scheduled_automatically(self):
        source=(Path(__file__).parent/'app.py').read_text(encoding='utf-8')
        tree=ast.parse(source)
        app=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=='App')
        init=next(node for node in app.body if isinstance(node,ast.FunctionDef) and node.name=='__init__')
        calls=[node for node in ast.walk(init) if isinstance(node,ast.Call)]
        afters=[node for node in calls if isinstance(node.func,ast.Attribute) and node.func.attr=='after']
        self.assertFalse(any(
            any(isinstance(arg,ast.Attribute) and arg.attr=='_check_content_updates' for arg in call.args)
            for call in afters
        ), 'Never schedule network update checks at startup.')
    def test_update_button_remains_available(self):
        source=(Path(__file__).parent/'app.py').read_text(encoding='utf-8')
        self.assertIn("self._check_content_updates,True",source)
    def test_asset_cache_is_bounded(self):
        source=(Path(__file__).parent/'app.py').read_text(encoding='utf-8')
        self.assertIn('max_cache_bytes=16*1024*1024',source)
if __name__=='__main__':unittest.main()
