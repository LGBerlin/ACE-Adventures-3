"""One-use scrolls teach supplemental, class-specific abilities without skipping levels."""
import game
SCROLLS={}
for school in game.SPELLS:
 name=school+" Sigil"
 SCROLLS["Scroll: "+name]={"ability":name,"level":6,"magic":school,"price":45}
for cls,paths in game.PATHS.items():
 if cls=="Mage":continue
 for path in paths:
  name=path+" Secret Art"
  SCROLLS["Scroll: "+name]={"ability":name,"level":6,"path":path,"price":45}
def stock():
 return {name:{"price":spec["price"],"description":"Class-specific training scroll (level 6)"} for name,spec in SCROLLS.items()}
def study(c,item):
 if not c.get("started") or c.get("enemy"):raise ValueError("Cannot study scrolls during battle.")
 h=c["characters"][c["active"]]
 if item not in h["inventory"] or item not in SCROLLS:raise ValueError("You do not own that training scroll.")
 spec=SCROLLS[item]
 if h["level"]<spec["level"]:raise ValueError("Your level is too low to study this scroll.")
 if "magic" in spec and (h["class"]!="Mage" or h["magic"]!=spec["magic"]):raise ValueError("Wrong magic school.")
 if "path" in spec and h["path"]!=spec["path"]:raise ValueError("Wrong class path.")
 name=spec["ability"]
 if name in h["moves"]:raise ValueError("Ability already learned.")
 h["moves"].append(name)
 h["inventory"].remove(item)
 msg=h["name"]+" learns "+name+"."
 c["history"].append(msg)
 c["turn"]+=1
 return msg
