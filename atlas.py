"""Deterministic local map model for the eventual parchment atlas UI.

Map state mirrors the quest engine. A click must go back through story.select;
this module never bypasses progression restrictions.
"""
import story

NODES = {
    "square": {"label": "Village Square", "x": 50, "y": 60},
    "tavern": {"label": "Lantern & Thistle", "x": 22, "y": 35},
    "market": {"label": "Yarrow's Apothecary", "x": 80, "y": 35},
    "well": {"label": "Old Well", "x": 45, "y": 18},
    "forest": {"label": "Ashwood Path", "x": 67, "y": 8},
}
ROADS = (("square", "tavern"), ("square", "market"), ("square", "well"), ("well", "forest"))
def state(campaign):
    active = campaign.get("location", "square")
    unlocked = {key for _, key in story.options(campaign) if key in NODES}
    return {
        "current": active,
        "nodes": [{**data, "id": key, "current": key == active,
                   "reachable": key in unlocked} for key, data in NODES.items()],
        "roads": [list(road) for road in ROADS],
    }
def travel(campaign, destination):
    if destination not in NODES:
        raise ValueError("Unknown destination on this map.")
    if campaign.get("enemy"):
        raise ValueError("You cannot travel while in combat.")
    if destination not in {key for _, key in story.options(campaign)}:
        raise ValueError("That destination is not yet accessible.")
    return story.select(campaign, destination)
