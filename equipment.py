"""Rules-owned weapon equipment, compatible with campaigns saved before equipment existed."""
WEAPONS = {
    "Iron Sword": {"classes": ("Fighter", "Vessel"), "attack": 1},
    "Daggers": {"classes": ("Rogue", "Fighter"), "attack": 1},
    "Ashwood Staff": {"classes": ("Mage", "Vessel"), "attack": 1},
    "Pilgrim Staff": {"classes": ("Vessel", "Mage", "Fighter"), "attack": 1},
}
def equipped(hero):
    item=hero.get("equipped_weapon")
    return item if item in WEAPONS and item in hero.get("inventory", []) else None
def equip(campaign,item):
    if not campaign.get("started"):raise ValueError("Start the campaign first.")
    if campaign.get("enemy"):raise ValueError("You cannot change equipment during a battle.")
    heroes=campaign["characters"]
    hero=heroes[campaign["active"]]
    if item not in WEAPONS:raise ValueError("That item cannot be equipped as a weapon.")
    if item not in hero["inventory"]:raise ValueError("You do not own that weapon.")
    if hero["class"] not in WEAPONS[item]["classes"]:raise ValueError("This class cannot equip that weapon.")
    hero.setdefault("gear_slots",{}).pop("weapon",None)
    hero["equipped_weapon"]=item
    message=f"{hero['name']} equips {item}."
    campaign["history"].append(message)
    campaign["turn"]+=1
    return message
def unequip(campaign):
    if campaign.get("enemy"):raise ValueError("You cannot change equipment during a battle.")
    hero=campaign["characters"][campaign["active"]]
    if not equipped(hero):raise ValueError("No weapon is equipped.")
    hero.pop("equipped_weapon",None)
    message=f"{hero['name']} puts away their weapon."
    campaign["history"].append(message)
    campaign["turn"]+=1
    return message
def attack_bonus(hero):
    item=equipped(hero)
    return WEAPONS[item]["attack"] if item else 0
