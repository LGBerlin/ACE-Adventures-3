"""Deterministic quest progression, separate from the narrative model."""
import dungeon_master
import json
from pathlib import Path
STAGES=('Speak with Elder Sera','Question Mira at the Lantern & Thistle','Inspect the old well','Confront the Hollow Guardian','Report to Elder Sera')
PLACES={'square':('Village Square','Elder Sera'), 'tavern':('Lantern & Thistle','Mira'), 'market':('Apothecary','Yarrow'), 'well':('Old Well',''), 'forest':('Ashwood Path','')}
DEFAULT_FLAVOUR={
 'square':'The sound of distant bells drifts over rain-dark cobblestones.',
 'tavern':'The hearth glows, and the innkeeper watches every stranger.',
 'market':'Bundles of dried herbs hang above the crowded shop counter.',
 'well':'Moss grows thick between the weathered stones.',
 'forest':'The roots twist across the path, as if guarding something below.'}

def flavour(c,root):
    """Optional data-only scene prose from the activated content pack."""
    place=c.get('location','square')
    fallback=DEFAULT_FLAVOUR.get(place,'')
    try:
        import update_addons
        path=update_addons.active_asset(root,'stories/hollow-bell.json')
        if path is None or path.stat().st_size>120_000:return fallback
        data=json.loads(path.read_text(encoding='utf-8'))
        loc=data.get('locations',{})
        text=loc.get(place)
        return text if isinstance(text,str) and 0<len(text)<=500 else fallback
    except (OSError,ValueError,TypeError,KeyError):return fallback

def ensure(c):
    c.setdefault('quest',{'stage':0,'completed':False});return c['quest']
def journal(c):
    q=ensure(c);return 'Quest complete · The Hollow Bell' if q['completed'] else 'The Hollow Bell · '+STAGES[q['stage']]
def options(c):
    q=ensure(c);p=c.get('location','square');s=q['stage']
    if c.get('enemy'):return [('Attack the guardian','attack'),('Try to negotiate','negotiate'),('Guard and observe','guard')]
    if p=='square':return ([('Speak with Elder Sera','elder')] if s in (0,4) else [])+[('Enter the Lantern & Thistle','tavern'),('Visit Yarrow’s Apothecary','market')]+([('Follow the lane to the well','well')] if s>=2 else [])
    if p=='tavern':return [('Question Mira about the bell','mira'),('Return to the square','square')]
    if p=='market':return [('Ask Yarrow about the ruins','yarrow'),('Buy a healing draught (9 gold)','buy_potion'),('Return to the square','square')]
    if p=='well':return [('Examine the carvings','runes')]+([('Follow tracks to Ashwood','forest')] if s>=3 else [])+[('Return to the square','square')]
    if p=='forest':return [('Approach the ruined arch','encounter'),('Return to the well','well')]
    return []
def select(c,choice):
    q=ensure(c);s=q['stage'];p=c.get('location','square')
    if choice in PLACES:
        permitted={a for _,a in options(c)}
        if choice not in permitted:raise ValueError('That route is not available yet. Follow the clues.')
        c['location']=choice
        import town_services
        town_services.note_travel(c,choice)
        msg={'square':'You return to the cobblestone square, beneath the silent belfry.','tavern':'The inn smells of cider and wet wool. Mira watches the door.','market':'Yarrow sorts remedies beneath strings of dried herbs.','well':'The mossy stone well stands alone under crooked branches.','forest':'Ashwood grows quiet around a broken stone arch.'}[choice]
    elif choice=='elder' and p=='square' and choice in {a for _,a in options(c)}:
        if s==0:q['stage']=1;msg='Elder Sera asks you to investigate the tolling bell. Mira at the inn heard it first.';dungeon_master.discover(c,'Mira heard the bell first.')
        elif s==4:q['completed']=True;msg='The village elder thanks the party. The Hollow Bell is finally silent. Quest complete!'
        else:msg='Elder Sera urges you to follow the clues you have uncovered.'
    elif choice=='mira' and p=='tavern' and choice in {a for _,a in options(c)}:
        if s==1:q['stage']=2;msg='Mira admits hearing the sound rise from the sealed well. She points toward the northern lane.';dungeon_master.discover(c,'The bell sounds from the sealed well.')
        else:msg='Mira pours a fresh drink and asks whether you found the well.'
    elif choice=='yarrow' and p=='market':msg='Yarrow remembers a guardian bound to an old ruin among the pines.'
    elif choice=='buy_potion' and p=='market':
        import merchant
        msg=merchant.buy(c,'Healing Draught')
    elif choice=='runes' and p=='well' and choice in {a for _,a in options(c)}:
        if s==2:q['stage']=3;msg='The carved runes name a Hollow Guardian. Fresh tracks run into Ashwood.';dungeon_master.discover(c,'Fresh tracks lead to Ashwood and the Hollow Guardian.')
        else:msg='The carved warning is still there, beneath the damp moss.'
    elif choice=='encounter' and p=='forest' and s==3:
        import game
        game.encounter(c);msg='The Hollow Guardian emerges to bar your passage.'
    elif choice in ('attack','guard','negotiate') and c.get('enemy'):
        import game
        text={'attack':'I attack the Hollow Guardian','guard':'I defend myself and watch the guardian','negotiate':'I try to persuade the guardian to stand down'}[choice]
        result=game.action(c,text);msg=result['result']
        if not c.get('enemy'):q['stage']=4;c['location']='square';msg+=' The guardian falls. Return to Elder Sera.'
    else:raise ValueError('That action is unavailable here.')
    npc={'elder':'sera','mira':'mira','yarrow':'yarrow'}.get(choice)
    if npc:dungeon_master.remember(c,npc,choice,msg)
    c['history'].append(msg)
    return msg