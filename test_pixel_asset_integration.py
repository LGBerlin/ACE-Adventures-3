"""The illustrated screens use indexed approved assets without bypassing game rules."""
import ast
import unittest
from pathlib import Path

class PixelAssetIntegrationTests(unittest.TestCase):
 def setUp(self):
  tree=ast.parse((Path(__file__).parent/'app.py').read_text(encoding='utf-8'))
  app=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=='App')
  self.methods={node.name:ast.get_source_segment((Path(__file__).parent/'app.py').read_text(encoding='utf-8'),node) for node in app.body if isinstance(node,ast.FunctionDef)}
 def test_scene_and_party_use_indexed_art(self):
  self.assertIn("self._pixel_asset(cv,'background'",self.methods['_scene'])
  self.assertIn('self._portrait(portrait,h)',self.methods['_adventure'])
 def test_inventory_and_shop_hooks_exist(self):
  self.assertIn('self._item_art(line,thing)',self.methods['_sidebar'])
  self.assertIn('self._item_art(line,item)',self.methods['_sidebar'])
 def test_trades_use_engine(self):
  self.assertIn('merchant.buy(self.c,item)',self.methods['_trade'])
  self.assertIn('merchant.sell(self.c,item)',self.methods['_trade'])
 def test_art_never_changes_rules(self):
  self.assertNotIn('game.save(',self.methods['_pixel_asset'])
  self.assertNotIn('merchant.buy(',self.methods['_pixel_asset'])
if __name__=='__main__':unittest.main()
