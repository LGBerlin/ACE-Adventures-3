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
 if spec["kind"]=="weapon":h.pop("equipped_weapon",None)
 slots[spec["kind"]]=item
 c["history"].append(h["name"]+" equips "+item+".")
 c["turn"]+=1
 return c["history"][-1]
def bonuses(h):
 result={"attack":0,"defense":0,"mana":0}
 for kind,item in h.get("gear_slots",{}).items():
  spec=ITEMS.get(item)
  if spec and spec["kind"]==kind and item in h.get("inventory",[]) and h["class"] in spec["classes"]:
   for field in result:
    relevant=(field=="attack" and kind=="weapon") or (field=="defense" and kind=="armor") or (field=="mana" and kind=="trinket")
    result[field]+=spec.get(field,0)
    level=h.get("enchantments",{}).get(item,0)
    affinity=h.get("enchant_types",{}).get(item)
    affinity_stat={"Ember":"attack","Frost":"defense","Storm":"mana","Fortitude":"defense","Arcane":"mana","Fortune":"attack"}.get(affinity)
    if level and field==affinity_stat:result[field]+=level
 return result
ENCHANT_TYPES=('Ember','Frost','Storm','Fortitude','Arcane','Fortune')
def enchant(c,item,rng=None):
 h=hero_for(c)
 if c.get("location")!="market":raise ValueError("Visit the town enchanter at the market.")
 if item not in h["inventory"] or item not in ITEMS:raise ValueError("Bring equipment you own.")
 level=h.setdefault("enchantments",{}).get(item,0)
 if level>=3:raise ValueError("Maximum enchantment reached.")
 cost=15*(level+1)
 if h["gold"]<cost:raise ValueError("Not enough gold to enchant.")
 import random
 spin=(rng or random.Random()).randrange(len(ENCHANT_TYPES))
 kind=ENCHANT_TYPES[spin]
 h["gold"]-=cost;h["enchantments"][item]=level+1
 h.setdefault("enchant_types",{})[item]=kind
 c["last_enchant_spin"]={"item":item,"slot":spin,"outcome":kind,"level":level+1}
 msg=h["name"]+" spins the enchantment wheel: "+kind+" +"+str(level+1)+" on "+item+"."
 c["history"].append(msg);c["turn"]+=1
 return msg
