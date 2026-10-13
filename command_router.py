"""Deterministic command routing for the fixed Tkinter user interface.

The Dungeon Master may narrate an event, but may not invent screens, mutate
character sheets or choose images. Only the Python game/interaction engine
executes actions. UI commands are explicit and cannot bypass active combat.
"""
import re

PANEL_ALIASES = {
    'Record': ('character sheet','character profile','my character','stats','character stats'),
    'Pack': ('inventory','my bag','backpack','equipment','my items'),
    'Abilities': ('abilities','spells','my spells','spellbook','skills','skill tree'),
    'Shop': ('shop','merchant store','open shop'),
    'Town': ('town services','town menu'),
    'Map': ('world map','show map','open map'),
    'Dice Board': ('dice board','dice tray','roll history'),
    'Story Tree': ('story tree','story map'),
    'Journal': ('journal','quest journal','quest log'),
}
UI_PREFIX = re.compile(r'^(?:please\s+)?(?:show|open|view|display|check|look at)\s+(?:me\s+)?(?:my\s+|the\s+)?', re.I)
SPELL = re.compile(r'^(?:i\s+)?(?:cast|use|invoke)\s+(?:a\s+|the\s+|my\s+)?([\w \-]+?)(?:\s+(?:at|on|toward|towards)\s+.+)?[.!]?$',re.I)

def route(text, campaign):
    """Return {kind,panel/text} without changing any campaign state."""
    if not isinstance(text,str) or not text.strip():
        raise ValueError('Describe what you want to do.')
    text=text.strip()
    normalized=' '.join(text.casefold().strip('.!? ').split())
    ui=UI_PREFIX.sub('',normalized)
    if ui != normalized:
        for panel, aliases in PANEL_ALIASES.items():
            if ui in aliases:
                if campaign.get('enemy') and panel in ('Shop','Town','Map'):
                    raise ValueError('Finish the encounter before opening town services or travelling.')
                return {'kind':'panel','panel':panel}
    match=SPELL.match(text)
    if match and campaign.get('characters'):
        hero=campaign['characters'][campaign['active']]
        name=' '.join(match.group(1).casefold().split())
        if name == 'fire ball':
            name='fireball'
        # Exact learned ability names are authoritative; keep the original
        # command and target so the rules engine and combat log can use them.
        learned={move.casefold():move for move in hero.get('moves',())}
        if name in learned:
            return {'kind':'action','text':text}
        if name=='fireball':
            raise ValueError('Fireball is not learned. Open Abilities to see available spells.')
        # All other unknown spells stay on the existing rules-validation path.
    return {'kind':'action','text':text}
