import random,unittest
import tkinter as tk
import game,ui_inventory,ui_shop
class MarketAndInventoryUITests(unittest.TestCase):
 def test_actual_inventory_shop_windows(self):
  try:root=tk.Tk()
  except tk.TclError as e:self.skipTest(str(e))
  root.withdraw()
  try:
   c=game.new_campaign('Test',1)
   h=game.character('Mara',22,'Rogue',random.Random(1))
   game.add_hero(c,h);game.start(c)
   seen=[]
   def texts(widget):
    if isinstance(widget,tk.Label):seen.append(widget.cget('text'))
    for ch in widget.winfo_children():texts(ch)
   inv=ui_inventory.open_inventory(root,c,lambda:None)
   root.update_idletasks()
   texts(inv)
   self.assertTrue(any('ADVENTURER' in x for x in seen))
   self.assertTrue(any('Weapon' in x for x in seen))
   inv.destroy()
   c['location']='market'
   seen.clear()
   market=ui_shop.open_shop(root,c,lambda:None)
   root.update_idletasks()
   texts(market)
   self.assertTrue(any('APOTHECARY' in x for x in seen))
   self.assertTrue(any(x=='BUY' for x in seen))
   market.destroy()
  finally:root.destroy()
