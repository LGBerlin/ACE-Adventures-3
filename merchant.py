"""Authoritative tabletop merchant economy.

Merchants change only deterministic campaign state; the Dungeon Master narrates
transactions but cannot award gold or inventory directly.
"""
CATALOG = {
    "Healing Draught": {"price": 9, "description": "Restore up to 12 HP."},
    "Health Potion": {"price": 7, "description": "Restore up to 8 HP."},
    "Travel Rations": {"price": 3, "description": "Supplies for the road."},
    "Iron Sword": {"price": 18, "description": "Reliable fighter's blade."},
    "Daggers": {"price": 12, "description": "A matched pair of short blades."},
    "Ashwood Staff": {"price": 14, "description": "A mage's carved focus."},
    "Pilgrim Staff": {"price": 11, "description": "A traveller's dependable staff."},
}
def available(campaign):
    return bool(campaign.get("started") and campaign.get("location") == "market"
                and not campaign.get("enemy"))
def _hero(campaign):
    if not available(campaign):
        raise ValueError("Trading requires visiting Yarrow's Apothecary outside combat.")
    index = campaign.get("active", 0)
    heroes = campaign.get("characters", [])
    if not isinstance(index, int) or not 0 <= index < len(heroes):
        raise ValueError("Choose a party member first.")
    return heroes[index]
def buy(campaign, item):
    hero = _hero(campaign)
    if item not in CATALOG:
        raise ValueError("The merchant does not stock that item.")
    price = CATALOG[item]["price"]
    if hero["gold"] < price:
        raise ValueError("Not enough gold.")
    hero["gold"] -= price
    hero["inventory"].append(item)
    result = f"{hero['name']} buys {item} for {price} gold."
    campaign["history"].append(result)
    campaign["turn"] += 1
    return result
def sell(campaign, item):
    hero = _hero(campaign)
    if item not in CATALOG or item not in hero["inventory"]:
        raise ValueError("The merchant will not buy that item.")
    price = max(1, CATALOG[item]["price"] // 2)
    hero["inventory"].remove(item)
    hero["gold"] += price
    result = f"{hero['name']} sells {item} for {price} gold."
    campaign["history"].append(result)
    campaign["turn"] += 1
    return result
