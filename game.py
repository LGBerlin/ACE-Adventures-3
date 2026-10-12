import copy, json, random, uuid, re
from pathlib import Path

PATHS={'Rogue':['Thief','Ranger','Assassin','Arcane Trickster'],'Mage':['Elementalist','Spellweaver','Runesage'],'Fighter':['Martial Artist','Knight','Swordsman','Barbarian','Paladin'],'Vessel':['Monk','Druid','Spirit Fighter','Warden','Oracle Vessel']}
SPELLS={'Earth':['Pebble Shot','Mud Slap','Ground Tremble'],'Water':['Water Shot','Splash','Ice Shard'],'Air':['Wind Gust','Air Cutter','Air Twist'],'Fire':['Flame Flick','Firewall','Heat Wave'],'Lightning':['Static Shock','Electric Whip','Lightning Dash'],'Gravity':['Gravitational Push','Downfall','Micro-Psychokinesis'],'Blood':['Sanguine Strike','Hemorrhage','Blood Drain'],'Illusion':['Mirage','Phantom Strike','Shape Shift'],'Light':['Blinding Light','Heavenly Bullet','Divine Shield'],'Dark':['Shadow Step','Nightmare','Dark Pulse'],'Support':['Healing Wave','Protective Aura','Mana Boost'],'Time':['Slow Mo Bubble','Temporal Shift','Chrono Dash'],'Creation':['Construct','Materialize','Form'],'Chaos':['Mind Jumble','Randomize','Unpredictable Strike']}
MOVES={'Thief':['Quick Hands','Pocket Sand','Nimble Escape'],'Ranger':['Quick Shot','Track','Woodland Step'],'Assassin':['Backstab','Silent Step','Weakpoint'],'Arcane Trickster':['Minor Mirage','Phantom Hand','Illusory Feint'],'Martial Artist':['Palm Strike','Counter Stance','Sweeping Kick'],'Knight':['Shield Bash','Guard','Defensive Advance'],'Swordsman':['Precision Cut','Blade Parry','Riposte'],'Barbarian':['Wild Swing','War Cry','Brutal Charge'],'Paladin':['Sacred Strike','Minor Blessing','Guardian Stance'],'Monk':['Palm Strike','Breath Focus','Spirit Guard'],'Druid':['Vine Snare','Seed Spark','Nature Touch'],'Spirit Fighter':['Soul Jab','Spirit Ward','Echo Step'],'Warden':['Guardian Step','Root Guard','Staff Sweep'],'Oracle Vessel':['Omen Glimpse','Fate Nudge','Whisper Ward']}
SKILLS=['Perception','Stealth','Acrobatics','Athletics','Persuasion','Investigation','Arcana','Insight','Survival','Nature']
TOWN={'tavern':{'npc':'Mira the Innkeeper','text':'The hearth crackles. Mira knows rumours of a stolen bell.'},'market':{'npc':'Oren the Merchant','text':'A merchant displays potions and worn swords.'},'gate':{'npc':'Captain Rowan','text':'A guard keeps watch at the forest gate.'},'square':{'npc':'Elder Sera','text':'Villagers gather by the silent bell tower.'}}

def display_archetype(hero):
    """Narrative role, never a fifth selectable class."""
    if hero.get('class')=='Mage' and hero.get('magic')=='Support':
        return 'Cleric'
    if hero.get('class')=='Rogue' and hero.get('path')=='Ranger':
        return 'Ranger'
    return hero.get('path') or hero.get('class','Adventurer')

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
    return {'id':uuid.uuid4().hex,'name':name.strip(),'age':int(age),'class':kind,'path':path,'magic':magic,'level':1,'xp':0,'stats':stats,'hp':hp,'max_hp':hp,'mana':mana,'max_mana':mana,'skills':rng.sample(SKILLS,4),'moves':list(SPELLS[magic]) if kind=='Mage' else list(MOVES[path]),'passives':[path+' Training'],'inventory':['Travel Rations',{'Rogue':'Daggers','Mage':'Ashwood Staff','Fighter':'Iron Sword','Vessel':'Pilgrim Staff'}[kind]],'gold':rng.randint(7,30),'sprite_seed':rng.randrange(2**31)}

def award_experience(hero,amount):
    """Award XP via verified game rules, never from LLM narration."""
    if not isinstance(amount,int) or isinstance(amount,bool) or amount<0 or amount>10000:
        raise ValueError('Invalid experience award')
    if hero['level']>=100:return []
    hero['xp']+=amount
    changes=[]
    while hero['level']<100 and hero['xp']>=70*hero['level']+12*hero['level']**2:
        hero['xp']-=70*hero['level']+12*hero['level']**2
        hero['level']+=1
        hero['max_hp']+=3
        hero['hp']=min(hero['max_hp'],hero['hp']+3)
        hero['max_mana']+=3
        hero['mana']=min(hero['max_mana'],hero['mana']+3)
        if hero['level']%10==0:
            stat={'Fighter':'STR','Rogue':'DEX','Mage':'INT','Vessel':'WIS'}[hero['class']]
            hero['stats'][stat]=min(30,hero['stats'][stat]+1)
            changes.append(stat+' increased')
        if hero['level'] in (8,16,28,40,55,70,85,100):
            passive=hero['path']+' Mastery '+str(hero['level'])
            if passive not in hero['passives']:
                hero['passives'].append(passive)
                changes.append(passive)
        if hero['class']=='Mage' and hero.get('magic') in SPELLS:
            import spell_catalog
            for name in spell_catalog.unlocked(hero['magic'],hero['level']):
                if name not in hero['moves']:
                    hero['moves'].append(name)
                    changes.append(name)
        elif hero['class'] in ('Fighter','Rogue','Vessel'):
            import technique_catalog
            for name in technique_catalog.unlocked(hero['path'],hero['level']):
                if name not in hero['moves']:
                    hero['moves'].append(name)
                    changes.append(name)
    if hero['level']==100:hero['xp']=0
    return changes

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
    if c.get('quest',{}).get('stage')==3:
        c['enemy']={'name':'Hollow Guardian','hp':30,'max_hp':30,'ac':14,'boss':True,'pos':[5,2]}
    c['history'].append('An enemy blocks the forest road. Battle begins!')
    import combat_log
    combat_log.append(c,actor=c['enemy']['name'],kind='encounter',description='A hostile creature appears.',hp=c['enemy']['hp'])

def enemy_response(c,hero,rng,guard=0):
    """Single authoritative enemy reaction shared by attacks, guard, spells and items."""
    enemy=c.get('enemy')
    if not enemy:return ''
    import loot_system
    phase=2 if enemy.get('boss') and enemy['hp']<=enemy.get('max_hp',30)//2 else 1
    if enemy.get('boss'):
        enemy['phase']=phase
        move='Bellshock' if phase==2 else 'Guardian Slam'
        rolled=rng.randint(2,5) if phase==2 else rng.randint(1,4)
    else:
        move='Counterattack'
        rolled=rng.randint(1,4)
    if enemy.pop('weakened',False):
        rolled=max(0,rolled-2)
    defense=loot_system.bonuses(hero)['defense']
    if enemy.pop('staggered',False):
        return 'The enemy is staggered and cannot retaliate.'
    ward=hero.get('ward_charges',0)
    if ward:
        hero['ward_charges']=ward-1
        defense+=3
    damage=max(0,rolled-max(0,guard)-defense)
    hero['hp']=max(0,hero['hp']-damage)
    if not any(member['hp']>0 for member in c['characters']):
        c['party_defeated']=True
    prefix='Boss uses '+move+'. ' if enemy.get('boss') else ''
    return prefix+('Enemy retaliates for '+str(damage)+' HP.' if damage else 'The attack is blocked.')

def retreat_to_town(c):
    """Emergency defeat recovery, without defeating the enemy or granting rewards."""
    if not c.get('started') or not c.get('enemy'):raise ValueError('Retreat requires an active encounter.')
    if not c.get('party_defeated'):raise ValueError('Retreat is only available after the whole party falls.')
    c['enemy']=None
    c['location']='square'
    c['party_defeated']=False
    for hero in c['characters']:
        hero['hp']=max(1,hero['max_hp']//4)
        hero['mana']=max(0,hero['max_mana']//4)
        hero['gold']=max(0,hero['gold']-3)
    c['turn']+=1
    msg='The village healers retrieve the defeated party. Everyone recovers to one-quarter health; each loses up to 3 gold.'
    c['history'].append(msg)
    return msg

def use_item(c,item,hero_index=None,rng=None):
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
    if c.get('enemy'):
        # Consuming supplies during battle takes the character's turn.
        # Prevent free unlimited healing while a hostile opponent remains.
        attacker=rng or random.Random()
        message+=' '+enemy_response(c,hero,attacker)
    c['history'].append(message)
    c['turn']+=1
    if c.get('enemy'):
        import combat_log
        combat_log.append(c,actor=hero['name'],kind='item',description=message,hp=hero['hp'])
    return message

def action(c,text,rng=None):
    rng=rng or random.Random();text=text.strip()
    if not c['started']:raise ValueError('Start the campaign first.')
    if not text:raise ValueError('Describe your action.')
    hero=c['characters'][c['active']];t=text.lower()
    if hero['hp']==0:raise ValueError('This character is incapacitated.')
    known=next((m for m in hero['moves'] if re.search(r'(?<!\w)'+re.escape(m.lower())+r'(?!\w)',t)),None)
    # Never let typed names of future skills bypass level requirements.
    if hero.get('class')=='Mage' and hero.get('magic') in SPELLS:
        import spell_catalog
        future=spell_catalog.catalog(hero['magic'])
    elif hero.get('class') in ('Fighter','Rogue','Vessel'):
        import technique_catalog
        future=technique_catalog.catalog(hero['path'])
    else:
        future=[]
    for entry in future:
        if entry['level']>hero['level'] and re.search(r'(?<!\w)'+re.escape(entry['name'].lower())+r'(?!\w)',t):
            raise ValueError('That technique or spell is not unlocked at your level.')
    # Names from *other* schools and paths are not free-form generic checks.
    # This prevents class/school spoofing by typing another archetype's move.
    all_named={name for names in SPELLS.values() for name in names}
    all_named.update(name for names in MOVES.values() for name in names)
    import spell_catalog, technique_catalog
    for school in SPELLS:
        all_named.update(entry['name'] for entry in spell_catalog.catalog(school))
    for path in technique_catalog.TECHNIQUES:
        all_named.update(entry['name'] for entry in technique_catalog.catalog(path))
    explicitly_named=bool(re.match(r'^(?:i\s+)?(?:use|cast|invoke|perform)\b',t))
    if explicitly_named:
        for ability in all_named:
            if ability not in hero['moves'] and re.search(r'(?<!\w)'+re.escape(ability.lower())+r'(?!\w)',t):
                raise ValueError('That spell or technique is not available to this character.')
    if any(x in t for x in ['teleport','stop time','resurrect']):raise ValueError('This exceeds your known Level 1 abilities.')
    if any(x in t for x in ['cast ','spell','fireball']) and not known and hero['magic']=='None':raise ValueError('Your character does not have that magic.')
    import ability_effects
    ability_role=ability_effects.role(hero,known)
    defensive=bool(c.get('enemy')) and (ability_role=='ward' or (not known and any(re.search(r'(?<!\w)'+w+r'(?!\w)',t) for w in ('guard','defend','block','take cover'))))
    cost=3 if known and not defensive else 0
    if cost:
        import loot_system
        # A magic focus reduces the effort to invoke learned abilities,
        # without permitting free unlimited spellcasting.
        cost=max(1,cost-min(2,loot_system.bonuses(hero)['mana']))
    # Learned techniques use the same resource and attack rules as spells.
    # An ability with a defensive name remains a guard, not a free attack.
    if hero['mana']<cost:raise ValueError('Not enough mana.')
    attack=bool(c['enemy']) and not defensive and (bool(known) or any(x in t for x in ['attack','shoot','stab','slash','strike','hit ','punch','kick']))
    social=any(x in t for x in ['persuad','convinc','negotia','bargain','talk to'])
    sneak=any(x in t for x in ['sneak','hide','escape','dodge'])
    stat='CHA' if social else 'INT' if hero['class']=='Mage' and known else 'DEX' if sneak or hero['class']=='Rogue' and attack else 'STR' if attack else 'WIS'
    modifier=(hero['stats'][stat]-10)//2
    if attack:
        import equipment
        modifier+=equipment.attack_bonus(hero)
        import loot_system
        modifier+=loot_system.bonuses(hero)['attack']
    dc=c['enemy']['ac'] if attack else 13
    roll=rng.randint(1,20);total=roll+modifier
    degree='Critical Success' if roll==20 else 'Critical Failure' if roll==1 else 'Exceptional Success' if total>=dc+5 else 'Success' if total>=dc else 'Partial Success' if total>=dc-3 else 'Failure'
    hero['mana']-=cost
    outcome=[]
    support_spell=ability_role in ('heal','mana') and bool(known)
    if support_spell:
        if degree in ('Success','Exceptional Success','Critical Success'):
            if ability_role=='mana':
                restored=min(hero['max_mana']-hero['mana'],4+hero['level'])
                hero['mana']+=restored
                outcome.append(f'{restored} mana restored.')
            else:
                restored=min(hero['max_hp']-hero['hp'],5+hero['level'])
                hero['hp']+=restored
                outcome.append(f'{restored} HP restored.')
        else:
            outcome.append('The support spell fails to take hold.')
        if c.get('enemy'):
            outcome.append(enemy_response(c,hero,rng))
    elif ability_role=='ward' and known:
        outcome.append(ability_effects.ward(hero,known,degree in ('Success','Exceptional Success','Critical Success')))
        if c.get('enemy'):outcome.append(enemy_response(c,hero,rng))
    elif attack:
        if degree in ('Success','Exceptional Success','Critical Success'):
            dmg=rng.randint(1,6)+max(0,modifier)
            if known:
                # Distinguish class actions from a basic weapon swing.
                # Bonus scales gently with progression and stays deterministic.
                dmg+=1+hero['level']//6+min(4,sum(' Mastery ' in p for p in hero.get('passives',[]))//2)
            if known and ability_role in ('damage','control'):
                bonus,flavour=ability_effects.offensive_effect(c,hero,known)
                dmg+=bonus
                if flavour:outcome.append(flavour)
            if roll==20:dmg*=2
            c['enemy']['hp']=max(0,c['enemy']['hp']-dmg);outcome.append(f'{dmg} damage inflicted.')
            if ability_role=='control' and c['enemy']['hp']>0:outcome.append(ability_effects.apply_control(c,hero,known,True))
        if c['enemy']['hp']==0:
            outcome.append('Enemy defeated, +10 XP to the victor, +5 XP to each surviving ally, +8 gold.')
            new_spells=award_experience(hero,10+max(0,(hero['stats'].get('INT',10)-10)//3))
            for ally in c['characters']:
                if ally is not hero and ally['hp']>0:
                    award_experience(ally,5+max(0,(ally['stats'].get('INT',10)-10)//4))
            hero['gold']+=8
            import loot_system
            pool=['Travel Rations','Health Potion','Wolf Fang','Greatsword','Guardian Ring']
            dropped=pool[rng.randint(0,len(pool)-1)]
            hero['inventory'].append(dropped)
            outcome.append('Loot: '+dropped+'.')
            c.setdefault('loot_history',[]).append({'item':dropped,'turn':c['turn'],'boss':bool(c['enemy'].get('boss'))})
            c['loot_history']=c['loot_history'][-100:]
            if c['enemy'].get('boss'):
                hero['inventory'].append('Hollow Guardian Relic')
                outcome.append('Boss trophy: Hollow Guardian Relic.')
            c['enemy']=None
            if new_spells:outcome.append('New spells learned: '+', '.join(new_spells)+'.')
        else:
            outcome.append(enemy_response(c,hero,rng))
    elif defensive:
        incoming_reduction=(2 if total>=dc else 1)+min(3,sum(' Mastery ' in p for p in hero.get('passives',[]))//3)
        message=enemy_response(c,hero,rng,guard=incoming_reduction) if c.get('enemy') else 'Guard stance held.'
        outcome.append('Guard stance reduces incoming damage. '+message)
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
            outcome.append(enemy_response(c,hero,rng,guard=2 if guarded else 0))
    result=f'D20 {roll} {modifier:+d} = {total}, DC {dc}: {degree}. '+' '.join(outcome)
    c['turn']+=1;c['history'].append(hero['name']+': '+text+'\n'+result)
    if c.get('enemy') or attack or defensive:
        import combat_log
        combat_log.append(c,actor=hero['name'],kind='action',description=result,hp=hero['hp'])
    return {'roll':roll,'modifier':modifier,'total':total,'dc':dc,'degree':degree,'result':result,'hero':hero['name'],'action':text}

def _valid_optional_gameplay(data):
    """Validate new gameplay fields while accepting saves from before they existed."""
    if data.get('guild_job') is not None:
        job=data['guild_job']
        if not isinstance(job,dict) or not isinstance(job.get('name'),str):return False
        import town_services
        if job['name'] not in town_services.JOBS:return False
        if not isinstance(job.get('start_turn'),int):return False
    if not isinstance(data.get('guild_jobs_completed',0),int) or data.get('guild_jobs_completed',0)<0:return False
    if data.get('party_defeated',False) not in (True,False):return False
    if data.get('town_memory') is not None:
        if not isinstance(data['town_memory'],dict):return False
        if any(not isinstance(v,int) or v<0 or v>100 for v in data['town_memory'].values()):return False
    for hero in data.get('characters',[]):
        if not isinstance(hero.get('level',1),int) or not 1<=hero.get('level',1)<=100:return False
        if not isinstance(hero.get('xp',0),int) or hero.get('xp',0)<0:return False
        if hero.get('gear_slots') is not None:
            if not isinstance(hero['gear_slots'],dict):return False
            import loot_system
            if any(kind not in ('weapon','armor','trinket') or item not in loot_system.ITEMS for kind,item in hero['gear_slots'].items()):return False
        if hero.get('enchantments') is not None:
            if not isinstance(hero['enchantments'],dict):return False
            if any(not isinstance(level,int) or not 0<=level<=3 for level in hero['enchantments'].values()):return False
    return True

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
                        for h in data['characters']) and _valid_optional_gameplay(data))
    except (KeyError,TypeError,ValueError,AttributeError):return False

def save(root,c):
    import os, shutil, tempfile
    if not _valid_campaign(c):raise ValueError('Invalid campaign state; refusing to overwrite save.')
    root=Path(root)
    target=root/'campaigns'
    if root.is_symlink() or target.is_symlink():
        raise ValueError('Refusing symbolic-link save storage.')
    target.mkdir(parents=True,exist_ok=True)
    p=target/(c['id']+'.json');backup=p.with_suffix('.bak')
    if p.is_symlink() or backup.is_symlink():
        raise ValueError('Refusing symbolic-link save files.')
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
    if d.is_symlink() or not d.exists():return out
    for p in sorted(d.glob('*.json')):
        for candidate in (p,p.with_suffix('.bak')):
            try:
                if candidate.is_symlink():continue
                if candidate.stat().st_size>5_000_000:continue
                data=json.loads(candidate.read_text(encoding='utf-8'))
                if _valid_campaign(data) and p.stem==data['id']:
                    out.append(data);break
            except (OSError,ValueError,UnicodeError,TypeError):pass
    return out