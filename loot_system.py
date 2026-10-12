"""Deterministic equipment catalog and town crafting services."""
ITEMS={
 "Chainmail":{"kind":"armor","classes":["Fighter","Vessel"],"defense":2,"price":35},
 "Leather Armor":{"kind":"armor","classes":["Rogue","Fighter"],"defense":1,"price":22},
 "Mystic Robe":{"kind":"armor","classes":["Mage","Vessel"],"mana":4,"price":30},
 "Runed Cloak":{"kind":"armor","classes":["Mage","Rogue","Vessel"],"defense":1,"price":38},
 "Wolf Fang":{"kind":"trinket","classes":["Rogue","Fighter"],"attack":1,"price":26},
 "Sage Amulet":{"kind":"trinket","classes":["Mage","Vessel"],"mana":3,"price":28},
 "Guardian Ring":{"kind":"trinket","classes":["Fighter","Vessel","Rogue","Mage"],"defense":1,"price":45},
 "Greatsword":{"kind":"weapon","classes":["Fighter"],"attack":3,"price":42},
 "Hunter Bow":{"kind":"weapon","classes":["Rogue"],"attack":2,"price":30},
 "Oak Staff":{"kind":"weapon","classes":["Mage","Vessel"],"attack":2,"price":25},
 "Twin Knives":{"kind":"weapon","classes":["Rogue","Fighter"],"attack":2,"price":27},
}
def hero_for(c):
 if not c.get("started") or c.get("enemy"):raise ValueError("Equipment management is unavailable now.")
 return c["characters"][c["active"]]
def equip(c,item):
 h=hero_for(c);spec=ITEMS.get(item)
 if not spec or item not in h["inventory"]:raise ValueError("Item not owned or cannot be equipped.")
 if h["class"] not in spec["classes"]:raise ValueError("Your class cannot equip that item.")
 slots=h.setdefault("gear_slots",{})
 slots[spec["kind"]]=item
 c["history"].append(h["name"]+" equips "+item+".")
 c["turn"]+=1
 return c["history"][-1]
def bonuses(h):
 result={"attack":0,"defense":0,"mana":0}
 for kind,item in h.get("gear_slots",{}).items():
  spec=ITEMS.get(item)
  if spec and spec["kind"]==kind and item in h.get("inventory",[]) and h["class"] in spec["classes"]:
   for field in result:result[field]+=spec.get(field,0)+ (h.get("enchantments",{}).get(item,0) if field=="attack" and kind=="weapon" else 0)
 return result
def enchant(c,item):
 h=hero_for(c)
 if c.get("location")!="market":raise ValueError("Visit the town enchanter at the market.")
 if item not in h["inventory"] or item not in ITEMS:raise ValueError("Bring equipment you own.")
 level=h.setdefault("enchantments",{}).get(item,0)
 if level>=3:raise ValueError("Maximum enchantment reached.")
 cost=15*(level+1)
 if h["gold"]<cost:raise ValueError("Not enough gold to enchant.")
 h["gold"]-=cost;h["enchantments"][item]=level+1
 msg=h["name"]+" enchants "+item+" to +"+str(level+1)+"."
 c["history"].append(msg);c["turn"]+=1
 return msg
