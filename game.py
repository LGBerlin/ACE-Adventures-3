import copy, json, random, uuid, re
from pathlib import Path

PATHS={'Rogue':['Thief','Ranger','Assassin','Arcane Trickster'],'Mage':['Elementalist','Spellweaver','Runesage'],'Fighter':['Martial Artist','Knight','Swordsman','Barbarian','Paladin'],'Vessel':['Monk','Druid','Spirit Fighter','Warden','Oracle Vessel']}
SPELLS={'Earth':['Pebble Shot','Mud Slap','Ground Tremble'],'Water':['Water Shot','Splash','Ice Shard'],'Air':['Wind Gust','Air Cutter','Air Twist'],'Fire':['Flame Flick','Firewall','Heat Wave'],'Lightning':['Static Shock','Electric Whip','Lightning Dash'],'Gravity':['Gravitational Push','Downfall','Micro-Psychokinesis'],'Blood':['Sanguine Strike','Hemorrhage','Blood Drain'],'Illusion':['Mirage','Phantom Strike','Shape Shift'],'Light':['Blinding Light','Heavenly Bullet','Divine Shield'],'Dark':['Shadow Step','Nightmare','Dark Pulse'],'Support':['Healing Wave','Protective Aura','Mana Boost'],'Time':['Slow Mo Bubble','Temporal Shift','Chrono Dash'],'Creation':['Construct','Materialize','Form'],'Chaos':['Mind Jumble','Randomize','Unpredictable Strike']}
MOVES={'Thief':['Quick Hands','Pocket Sand','Nimble Escape'],'Ranger':['Quick Shot','Track','Woodland Step'],'Assassin':['Backstab','Silent Step','Weakpoint'],'Arcane Trickster':['Minor Mirage','Phantom Hand','Illusory Feint'],'Martial Artist':['Palm Strike','Counter Stance','Sweeping Kick'],'Knight':['Shield Bash','Guard','Defensive Advance'],'Swordsman':['Precision Cut','Blade Parry','Riposte'],'Barbarian':['Wild Swing','War Cry','Brutal Charge'],'Paladin':['Sacred Strike','Minor Blessing','Guardian Stance'],'Monk':['Palm Strike','Breath Focus','Spirit Guard'],'Druid':['Vine Snare','Seed Spark','Nature Touch'],'Spirit Fighter':['Soul Jab','Spirit Ward','Echo Step'],'Warden':['Guardian Step','Root Guard','Staff Sweep'],'Oracle Vessel':['Omen Glimpse','Fate Nudge','Whisper Ward']}
SKILLS=['Perception','Stealth','Acrobatics','Athletics','Persuasion','Investigation','Arcana','Insight','Survival','Nature']
TOWN={'tavern':{'npc':'Mira the Innkeeper','text':'The hearth crackles. Mira knows rumours of a stolen bell.'},'market':{'npc':'Oren the Merchant','text':'A merchant displays potions and worn swords.'},'gate':{'npc':'Captain Rowan','text':'A guard keeps watch at the forest gate.'},'square':{'npc':'Elder Sera','text':'Villagers gather by the silent bell tower.'}}

def character(name,age,kind,rng=None):
    rng=rng or random.Random()
    if kind not in PATHS or not name.strip() or len(name)>32 or not 10<=int(age)<=120:raise ValueError('Enter a valid name, age (10–120) and class.')
    weights={'Rogue':[35,25,30,10],'Mage':[45,35,20],'Fighter':[25,25,24,18,8],'Vessel':[28,25,23,18,6]}[kind]
    path=rng.choices(PATHS[kind],weights)[0]
    magic='None'
    if kind=='Mage' or path=='Arcane Trickster':
        tier=rng.choices([0,1,2],[35,50,15])[0]
        magic=rng.choice([['Earth','Water','Fire','Air'],['Lightning','Gravity','Blood','Illusion','Light','Dark','Support'],['Time','Creation','Chaos']][tier])
    else:magic={'Monk':'Ki','Druid':'Nature','Warden':'Nature','Spirit Fighter':'Spirit','Oracle Vessel':'Omen','Paladin':'Light'}.get(path,'None')
    bonuses={'Rogue':[0,3,1,1,1,0],'Mage':[-1,1,0,3,2,1],'Fighter':[3,1,2,0,0,0],'Vessel':[1,2,2,1,2,0]}[kind]
    stats={k:max(6,min(20,rng.randint(8,15)+b)) for k,b in zip(['STR','DEX','CON','INT','WIS','CHA'],bonuses)}
    hp=max(8,{'Rogue':18,'Mage':13,'Fighter':25,'Vessel':21}[kind]+(stats['CON']-10)//2+rng.randint(-2,2))
    mana=max(0,{'Rogue':6,'Mage':24,'Fighter':3,'Vessel':15}[kind]+rng.randint(-2,3))
    return {'id':uuid.uuid4().hex,'name':name.strip(),'age':int(age),'class':kind,'path':path,'magic':magic,'race':rng.choice(['Human','Elf','Dwarf','Halfling','Orc','Tiefling','Gnome']),'level':1,'xp':0,'stats':stats,'hp':hp,'max_hp':hp,'mana':mana,'max_mana':mana,'skills':rng.sample(SKILLS,4),'moves':SPELLS[magic] if kind=='Mage' else MOVES[path],'passives':[path+' Training'],'inventory':['Travel Rations',{'Rogue':'Daggers','Mage':'Ashwood Staff','Fighter':'Iron Sword','Vessel':'Pilgrim Staff'}[kind]],'gold':rng.randint(7,30),'sprite_seed':rng.randrange(2**31)}

def new_campaign(title,players):
    if not title.strip() or len(title)>60 or not 1<=int(players)<=8:raise ValueError('Choose a campaign title and 1–8 players.')
    return {'id':uuid.uuid4().hex,'title':title.strip(),'players':int(players),'characters':[],'active':0,'started':False,'location':'square','town':copy.deepcopy(TOWN),'enemy':None,'history':[],'turn':0,'world_seed':random.randrange(2**31)}

def add_hero(c,hero):
    if c['started'] or len(c['characters'])>=c['players']:raise ValueError('Character roulette is locked for this party.')
    c['characters'].append(hero)

def start(c):
    if len(c['characters'])!=c['players']:raise ValueError('Create one character for each player first.')
    if not c['started']:
        c['started']=True;c['history'].append('The party arrives at Ironwood Square. The old bell rings, although its rope has vanished.')

def choose_location(c,place):
    if place not in TOWN:raise ValueError('Unknown location')
    c['location']=place;c['history'].append('Arrived at '+place.title()+'. '+TOWN[place]['text'])

def encounter(c,rng=None):
    rng=rng or random.Random()
    if c['enemy']:return
    c['enemy']={'name':rng.choice(['Moss Goblin','Thorn Wolf','Forest Wisp']),'hp':15,'max_hp':15,'ac':12,'pos':[5,2]}
    c['history'].append('An enemy blocks the forest road. Battle begins!')

def use_item(c,item,hero_index=None):
    """Use inventory items with authoritative, persisted effects.

    No AI response is allowed to directly change HP, inventory, or gold.
    """
    if not c['started']:raise ValueError('Start the campaign first.')
    index=c['active'] if hero_index is None else hero_index
    if not isinstance(index,int) or not 0<=index<len(c['characters']):raise ValueError('Unknown party member.')
    hero=c['characters'][index]
    effects={'Health Potion':8,'Healing Draught':12}
    if item not in effects:raise ValueError('That item cannot be consumed.')
    if item not in hero['inventory']:raise ValueError('You do not have that item.')
    if hero['hp']>=hero['max_hp']:raise ValueError('Already at full health.')
    if hero['hp']<=0:raise ValueError('An incapacitated character cannot use an item.')
    amount=min(effects[item],hero['max_hp']-hero['hp'])
    hero['hp']+=amount
    hero['inventory'].remove(item)
    message=f"{hero['name']} drinks {item} and restores {amount} HP."
    c['history'].append(message)
    c['turn']+=1
    return message

def action(c,text,rng=None):
    rng=rng or random.Random();text=text.strip()
    if not c['started']:raise ValueError('Start the campaign first.')
    if not text:raise ValueError('Describe your action.')
    hero=c['characters'][c['active']];t=text.lower()
    if hero['hp']==0:raise ValueError('This character is incapacitated.')
    known=next((m for m in hero['moves'] if re.search(r'(?<!\w)'+re.escape(m.lower())+r'(?!\w)',t)),None)
    if any(x in t for x in ['teleport','stop time','resurrect']):raise ValueError('This exceeds your known Level 1 abilities.')
    if any(x in t for x in ['cast ','spell','fireball']) and not known and hero['magic']=='None':raise ValueError('Your character does not have that magic.')
    defensive=bool(c.get('enemy')) and (bool(known and any(w in known.lower() for w in ('guard','ward','dodge','escape','stance','parry','counter'))) or any(re.search(r'(?<!\w)'+w+r'(?!\w)',t) for w in ('guard','defend','block','take cover')))
    cost=3 if known and not defensive else 0
    if hero['mana']<cost:raise ValueError('Not enough mana.')
    attack=bool(c['enemy']) and not defensive and (bool(known) or any(x in t for x in ['attack','shoot','stab','slash','strike','hit ','punch','kick']))
    social=any(x in t for x in ['persuad','convinc','negotia','bargain','talk to'])
    sneak=any(x in t for x in ['sneak','hide','escape','dodge'])
    stat='CHA' if social else 'INT' if hero['class']=='Mage' and known else 'DEX' if sneak or hero['class']=='Rogue' and attack else 'STR' if attack else 'WIS'
    modifier=(hero['stats'][stat]-10)//2
    dc=c['enemy']['ac'] if attack else 13
    roll=rng.randint(1,20);total=roll+modifier
    degree='Critical Success' if roll==20 else 'Critical Failure' if roll==1 else 'Exceptional Success' if total>=dc+5 else 'Success' if total>=dc else 'Partial Success' if total>=dc-3 else 'Failure'
    hero['mana']-=cost
    outcome=[]
    if attack:
        if degree in ('Success','Exceptional Success','Critical Success'):
            dmg=rng.randint(1,6)+max(0,modifier)
            if roll==20:dmg*=2
            c['enemy']['hp']=max(0,c['enemy']['hp']-dmg);outcome.append(f'{dmg} damage inflicted.')
        if c['enemy']['hp']==0:
            outcome.append('Enemy defeated, +10 XP, +8 gold.');hero['xp']+=10;hero['gold']+=8;c['enemy']=None
        else:
            dmg=rng.randint(1,4);hero['hp']=max(0,hero['hp']-dmg);outcome.append(f'Enemy retaliates for {dmg} HP.')
    elif defensive:
        incoming=rng.randint(1,4)
        reduction=2 if total>=dc else 1
        damage=max(0,incoming-reduction)
        hero['hp']=max(0,hero['hp']-damage)
        outcome.append(f'Guard stance reduces an incoming {incoming} damage to {damage}.')
    elif 'smoke' in t or 'cover' in t:
        if known and hero['magic']=='Fire' and any(x in t for x in ['leaves','grass','wood']) and total>=dc:
            c['smoke']=True;outcome.append('Flammable terrain catches, creating smoke cover.')
        else:outcome.append('You do not create effective smoke cover.')
    else:
        outcome.append('The attempt '+('works.' if total>=dc else 'has a complication.' if degree=='Partial Success' else 'fails.'))
        # A live opponent remains dangerous even if the adventurer negotiates,
        # hides, or tries another creative action. Avoid free infinite turns.
        if c.get('enemy'):
            guarded=any(re.search(r'(?<!\w)'+word+r'(?!\w)',t) for word in ('guard','defend','block','shield','dodge')) and total>=dc
            retaliation=max(0,rng.randint(1,4)-(2 if guarded else 0))
            hero['hp']=max(0,hero['hp']-retaliation)
            outcome.append(f'Enemy retaliates for {retaliation} HP.' if retaliation else 'Your guard prevents the counterattack.')
    result=f'D20 {roll} {modifier:+d} = {total}, DC {dc}: {degree}. '+' '.join(outcome)
    c['turn']+=1;c['history'].append(hero['name']+': '+text+'\n'+result)
    return {'roll':roll,'modifier':modifier,'total':total,'dc':dc,'degree':degree,'result':result,'hero':hero['name'],'action':text}

def _valid_campaign(data):
    """Never admit an arbitrary or partial JSON document as a playable save."""
    if not isinstance(data,dict):return False
    try:
        uuid.UUID(data['id'])
        return (isinstance(data['title'],str) and 0 < len(data['title'])<=60
                and isinstance(data['players'],int) and 1<=data['players']<=8
                and isinstance(data['characters'],list) and len(data['characters'])<=data['players']
                and isinstance(data['history'],list) and isinstance(data['started'],bool)
                and isinstance(data['active'],int)
                and (data['active']==0 if not data['characters'] else 0<=data['active']<len(data['characters']))
                and all(isinstance(h,dict) and isinstance(h.get('name'),str)
                        and h.get('class') in PATHS and isinstance(h.get('stats'),dict)
                        for h in data['characters']))
    except (KeyError,TypeError,ValueError,AttributeError):return False

def save(root,c):
    import os, shutil, tempfile
    if not _valid_campaign(c):raise ValueError('Invalid campaign state; refusing to overwrite save.')
    target=Path(root)/'campaigns';target.mkdir(parents=True,exist_ok=True)
    p=target/(c['id']+'.json');backup=p.with_suffix('.bak')
    raw=json.dumps(c,indent=2,ensure_ascii=False)
    if len(raw.encode('utf-8'))>5_000_000:raise ValueError('Campaign save exceeds limit.')
    # Back up only a readable save; a damaged file must never replace a good backup.
    if p.exists():
        try:
            old=json.loads(p.read_text(encoding='utf-8'))
            if _valid_campaign(old):shutil.copy2(p,backup)
        except (OSError,ValueError,UnicodeError):pass
    name=None
    try:
        with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=target,delete=False) as f:
            name=f.name;f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(name,p)
    finally:
        if name and Path(name).exists():Path(name).unlink()

def load_all(root):
    d=Path(root)/'campaigns';out=[]
    if not d.exists():return out
    for p in sorted(d.glob('*.json')):
        for candidate in (p,p.with_suffix('.bak')):
            try:
                if candidate.stat().st_size>5_000_000:continue
                data=json.loads(candidate.read_text(encoding='utf-8'))
                if _valid_campaign(data) and p.stem==data['id']:
                    out.append(data);break
            except (OSError,ValueError,UnicodeError,TypeError):pass
    return out