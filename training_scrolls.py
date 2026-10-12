"""Consumable training scrolls; class, school, and level checks are authoritative."""
import spell_catalog
import technique_catalog
def title_for(name):
 return "Scroll: "+name
def study(c,item):
 if not c.get("started") or c.get("enemy"):raise ValueError("Scrolls cannot be studied now.")
 hero=c["characters"][c["active"]]
 if item not in hero["inventory"] or not item.startswith("Scroll: "):raise ValueError("You do not own that scroll.")
 name=item[8:]
 if hero["class"]=="Mage":
  entries=spell_catalog.catalog(hero["magic"])
 else:
  entries=technique_catalog.catalog(hero["path"])
 match=next((e for e in entries if e["name"]==name),None)
 if not match:raise ValueError("This scroll is not compatible with your class.")
 if match["level"]>hero["level"]:raise ValueError("Your level is too low to understand this scroll.")
 if name in hero["moves"]:raise ValueError("You already know that ability.")
 hero["moves"].append(name)
 hero["inventory"].remove(item)
 message=hero["name"]+" learns "+name+" from a scroll."
 c["history"].append(message);c["turn"]+=1
 return message
def stock():
 # Scroll selection stays small and legal; different classes can find their own scrolls.
 import game
 return {title_for(spell_catalog.REGULAR[s]):{"price":36,"description":"Level 5 "+s+" spell"} for s in game.SPELLS}
