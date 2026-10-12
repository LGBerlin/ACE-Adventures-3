"""One free-text interaction path. Dice only for uncertain actions.

Never let narration or intent classification bypass the deterministic quest gates.
"""
import re
import game,story,dice_ledger,merchant,equipment

LOCATION_WORDS={
 'square':('square','town square','village square'),
 'tavern':('tavern','inn','lantern & thistle','lantern and thistle'),
 'market':('market','apothecary','shop','yarrow\'s shop'),
 'well':('well','old well'),
 'forest':('forest','ashwood','woods')}
TRAVEL=re.compile(r'^(?:i\s+)?(?:want to |would like to |will |am going to |decide to )?(?:go|walk|travel|head|move|return|visit|enter|follow|make my way|take the road)(?:\s+back)?\s+(?:to|toward|towards|into|over to|through|the|a)?\s*',re.I)
def interpret_simple(c,text):
    """Return a canonical quest choice, or None for uncertain actions."""
    lower=' '.join(text.casefold().strip().split())
    available={value for _,value in story.options(c)}
    travel=TRAVEL.match(lower)
    if travel:
        destination=lower[travel.end():].strip()
        destination=re.sub(r'^(?:to|the|a|into|toward|towards)\s+','',destination)
        for place,aliases in LOCATION_WORDS.items():
            if any(destination==alias or destination==('the '+alias) for alias in aliases):
                if place not in available:raise ValueError('That route is not available yet. Follow the clues.')
                return place
    # Social choices are deliberately limited to present NPCs, not remote dialogue.
    npc_verbs=('talk','speak','ask','question','converse','chat')
    if any(re.search(r'\b'+v+r'\b',lower) for v in npc_verbs):
        for choice,names in {'elder':('sera','elder'),'mira':('mira','innkeeper'),'yarrow':('yarrow','herbalist')}.items():
            if choice in available and any(re.search(r'\b'+name+r'\b',lower) for name in names):
                return choice
    if c.get('location')=='well' and 'runes' in available and any(w in lower for w in ('read the runes','examine the carvings','inspect the runes')):
        return 'runes'
    if c.get('location')=='market' and 'buy_potion' in available and any(w in lower for w in ('buy a healing draught','buy a potion','purchase a healing draught')):
        return 'buy_potion'
    if c.get('location')=='forest' and 'encounter' in available and any(w in lower for w in ('approach the ruined arch','approach the ruins')):
        return 'encounter'
    return None

def perform(c,text,rng=None):
    """Resolve player intent before using dice; all mutations remain rules-driven."""
    text=text.strip()
    if not text:raise ValueError('Describe what you want to do.')
    if not c.get('started'):raise ValueError('Start the campaign first.')
    lower=' '.join(text.casefold().split())
    # Combat always takes precedence. No travel, merchant or free social
    # interaction can silently bypass an active enemy turn.
    if c.get('enemy'):
        if re.match(r'^(?:i\s+)?(?:buy|purchase|sell|go|travel|walk|head|visit|return)\b',lower):
            raise ValueError('You must resolve the encounter before trading or travelling.')
        result=game.action(c,text,rng)
        result['roll_required']=True
        dice_ledger.record(c,result,text)
        return result
    choice=interpret_simple(c,text)
    if choice is not None:
        outcome=story.select(c,choice)
        return {'roll_required':False,'result':outcome,'choice':choice,'action':text}
    gear=re.fullmatch(r'(?:i\s+)?(?:want to |would like to |please )?(equip|wield|unequip|sheathe)\s*(?:my |the |a |an )?(.*?)[.!]?',lower)
    if gear:
        verb,name=gear.groups()
        if verb in ('unequip','sheathe'):
            msg=equipment.unequip(c)
        else:
            item=next((item for item in equipment.WEAPONS if item.casefold()==name.strip()),None)
            if item is None:raise ValueError('Unknown weapon.')
            msg=equipment.equip(c,item)
        return {'roll_required':False,'result':msg,'action':text,'choice':'equipment'}
    # Buy/sell are deterministic, and both the merchant and available funds
    # are checked by the shop engine, not the text interpreter or the AI.
    trade=re.fullmatch(r'(?:i\s+)?(?:want to |would like to |please )?(buy|purchase|sell)\s+(?:a |an |the |some )?(.+?)[.!]?',lower)
    if trade:
        verb,name=trade.groups()
        item=next((item for item in merchant.CATALOG if item.casefold()==name.strip()),None)
        if item is None:raise ValueError('The merchant does not trade that item.')
        msg=(merchant.sell if verb=='sell' else merchant.buy)(c,item)
        return {'roll_required':False,'result':msg,'action':text,'choice':'trade'}
    # Mundane observations, listening, and rest are not skill checks and
    # never provide free HP, mana, XP or equipment.
    mundane=re.fullmatch(r'(?:i\s+)?(?:look around|look at the scenery|wait|rest|sit down|listen|hello|hi|hey|thank you|thanks|examine my equipment|check my inventory|open my journal|view the map|study the map)[.!]?',lower)
    if mundane:
        msg='You '+lower.removeprefix('i ').rstrip('.!')+'.'
        c['history'].append(msg);c['turn']+=1
        return {'roll_required':False,'result':msg,'action':text}
    # Explicit dialogue with a non-present character is not a remote
    # charisma roll; ask the player to travel to them instead.
    if re.search(r'\b(?:talk|speak|ask|question|converse|chat)\b',lower):
        if re.search(r'\b(?:sera|elder|mira|innkeeper|yarrow|herbalist)\b',lower):
            raise ValueError('You must be with that person to speak to them.')
    result=game.action(c,text,rng)
    result['roll_required']=True
    dice_ledger.record(c,result,text)
    return result
