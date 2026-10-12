"""ACE Adventures 3 illustrated story-first native Tk interface."""
import json,queue,threading,tkinter as tk
from tkinter import messagebox
from pathlib import Path
import merchant,equipment,atlas,dice_ledger
import game,ai,story,art,ai_connections,addon_updates,update_addons,app_release_checker,comfy_art,asset_registry,story_tree,animation_director,visual_mapping,spell_catalog,technique_catalog,interaction
from io import BytesIO
DATA=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'
DARK='#241e1b';PARCH='#ecd9b0';INK='#3d2b22';BRASS='#b99152';WOOD='#513322';LIGHT='#f8e8c8'
class App(tk.Tk):
 def __init__(self):
  super().__init__();self.title('ACE Adventures III — The Hollow Bell');self.geometry('1300x880');self.minsize(960,700);self.configure(bg=DARK)
  self.c=None;self.busy=False;self.q=queue.Queue();self.panel='Record';self.last_roll=None;self.update_status='Not checked';self._sprite_refs=[];self.animation_director=animation_director.Director();self.last_visual_cue=None;self.asset_pack=asset_registry.Registry(DATA/'approved sprites',max_cache_bytes=16*1024*1024);self._poll_job=None;self._closed=False;self._load_asset_index();self._home();self._poll_job=self.after(400,self._poll)
 def _load_asset_index(self):
  index=DATA/'approved sprites'/'manifest.json'
  if index.is_file():
   try:self.asset_pack.load(index)
   except (OSError,ValueError):pass
 def _portrait(self,canvas,hero):
  """Static image only; never start a render loop in the story screen."""
  key=asset_registry.select_character_sprite(self.asset_pack,hero,'portrait')
  if key is None:key=asset_registry.select_character_sprite(self.asset_pack,hero,'body')
  source=self.asset_pack.bytes(key) if key else None
  if source:
   try:
    from PIL import Image,ImageTk
    with Image.open(BytesIO(source)) as img:
     img.thumbnail((168,168))
     photo=ImageTk.PhotoImage(img.copy(),master=canvas)
    canvas.create_image(122,90,image=photo)
    canvas.image=photo
    return
   except (ImportError,OSError,ValueError,tk.TclError):pass
  art.character(canvas,78,28,hero['class'],hero['sprite_seed'],4)
 def clear(self):
  for widget in self.winfo_children():widget.destroy()
 def label(self,parent,text,size=12,fg=INK,bg=PARCH,**kw):
  return tk.Label(parent,text=text,font=('Georgia',size,'bold' if size>=17 else 'normal'),fg=fg,bg=bg,justify='left',wraplength=kw.get('wraplength',0),anchor='w')
 def button(self,parent,text,fn,light=False):
  """Paint consistent high-contrast controls; macOS native buttons ignore bg."""
  bg='#f3e0b9' if light else '#553824'
  fg='#31251b' if light else '#fff1cf'
  control=tk.Label(parent,text=text,font=('Georgia',11,'bold'),bg=bg,fg=fg,
                   relief='raised',bd=2,highlightthickness=1,highlightbackground=BRASS,
                   padx=11,pady=8,cursor='hand2',takefocus=True)
  control.bind('<ButtonRelease-1>',lambda event:fn() if control.winfo_containing(event.x_root,event.y_root)==control else None)
  control.bind('<Return>',lambda event:fn())
  control.bind('<space>',lambda event:fn())
  return control
 def page(self,title):
  self.clear();bar=tk.Frame(self,bg='#33261e',height=72);bar.pack(fill='x')
  self.label(bar,'A.C.E.  ADVENTURES III    ✦',22,LIGHT,'#33261e').pack(side='left',padx=20,pady=12)
  self.label(bar,'❦  '+title.upper(),11,BRASS,'#33261e').pack(side='left',padx=14)
  self.button(bar,'THE CHRONICLES',self._home).pack(side='right',padx=12)
  self.button(bar,'AI CONNECTIONS',self._connections).pack(side='right',padx=5)
  self.button(bar,'CHECK UPDATES',self._check_content_updates).pack(side='right',padx=5)
 def card(self,parent,title=''):
  outer=tk.Frame(parent,bg=WOOD,bd=4,relief='ridge');inner=tk.Frame(outer,bg=PARCH,highlightbackground=BRASS,highlightthickness=2);inner.pack(fill='both',expand=True,padx=4,pady=4)
  if title:
   self.label(inner,'❧   '+title.upper()+'   ❧',14,fg='#78512f').pack(anchor='w',padx=16,pady=(14,7))
   tk.Frame(inner,bg=BRASS,height=2).pack(fill='x',padx=16,pady=(0,5))
  return outer,inner
 def _connections(self):
  """Probe optional services off the UI thread; leave campaigns untouched."""
  popup=tk.Toplevel(self);popup.title('AI Connections');popup.geometry('520x290');popup.configure(bg=WOOD)
  outer,inside=self.card(popup,'Local AI Connections');outer.pack(fill='both',expand=True,padx=12,pady=12)
  status=self.label(inside,'Checking Ollama and ComfyUI on this Mac...',13,wraplength=460)
  status.pack(anchor='w',padx=12,pady=16)
  self.label(inside,'Ollama: storytelling and action interpretation\nComfyUI: optional offline artwork generation (not live gameplay)',11,wraplength=450).pack(anchor='w',padx=12)
  self.label(inside,'Content updates: '+self.update_status,11,wraplength=450).pack(anchor='w',padx=12,pady=4)
  self.button(inside,'CHECK FOR CONTENT UPDATES',self._check_content_updates,True).pack(padx=12,pady=4)
  self.button(inside,'RESTORE PREVIOUS CONTENT',self._rollback_content,True).pack(padx=12,pady=4)
  self.button(inside,'CHECK APP RELEASES (MANUAL INSTALL)',self._check_app_releases,True).pack(padx=12,pady=4)
  self.button(inside,'GENERATE LOCATION ART (COMFYUI)',lambda:self._generate_scene(popup,status),True).pack(padx=12,pady=4)
  def worker():
   result=ai_connections.all_statuses(timeout=2)
   self.q.put(('services',(popup,status,result)))
  threading.Thread(target=worker,daemon=True).start()
 def _home(self):
  self.last_visual_cue=None;self.animation_director.clear();self.c=None;self.page('The Book of Unwritten Roads')
  body=tk.Frame(self,bg=DARK);body.pack(expand=True,fill='both',padx=18,pady=15)
  left,inside=self.card(body,'Campaign Library');left.pack(side='left',fill='y',padx=(0,12))
  self.button(inside,'✦  NEW CHRONICLE',self._new,True).pack(fill='x',padx=14,pady=9)
  for c in game.load_all(DATA):self.button(inside,c['title'],lambda c=c:self._open(c),True).pack(fill='x',padx=12,pady=5)
  right,content=self.card(body,'The Hollow Bell');right.pack(side='left',fill='both',expand=True)
  cv=tk.Canvas(content,height=360,bg=DARK,highlightthickness=0);cv.pack(fill='x',padx=12,pady=12);cv.bind('<Configure>',lambda e:self._scene(cv,'square'))
  self.label(content,'Beyond the last farms lies Briarhollow, where a bell rings without a bellringer.',20,wraplength=660).pack(anchor='w',padx=25,pady=15)
  self.label(content,'Choose your companions. Follow the clues. Roll the dice when the world pushes back.',13,wraplength=660).pack(anchor='w',padx=25)
 def _new(self):
  self.page('New Chronicle');outer,f=self.card(self,'Begin a New Adventure');outer.pack(padx=90,pady=40,fill='x')
  self.label(f,'Name your campaign',14).pack(pady=(10,3));name=tk.Entry(f,font=('Georgia',16));name.pack(fill='x',padx=45,pady=6)
  self.label(f,'Number of adventurers (1–8)',14).pack(pady=8);count=tk.Spinbox(f,from_=1,to=8,font=('Georgia',14),width=6);count.pack()
  def create():
   try:self.c=game.new_campaign(name.get(),int(count.get()));game.save(DATA,self.c);self._show()
   except ValueError as e:messagebox.showerror('Campaign',str(e))
  self.button(f,'OPEN THE CHRONICLE',create).pack(pady=22)
 def _open(self,c):self.last_visual_cue=None;self.animation_director.clear();self.c=c;story.ensure(self.c);self._show()
 def _show(self):
  if len(self.c['characters'])<self.c['players']:self._create_character()
  else:self._adventure()
 def _create_character(self):
  self.page('The Fates · Character Creation');outer,f=self.card(self,f'Adventurer {len(self.c["characters"])+1} of {self.c["players"]}');outer.pack(expand=True,padx=55,pady=18,fill='both')
  self.label(f,'You may choose your name, age and class. All other details are rolled once and are permanent.',13,wraplength=700).pack(padx=16,pady=10)
  row=tk.Frame(f,bg=PARCH);row.pack(pady=10);self.label(row,'Name',14).grid(row=0,column=0,padx=15);name=tk.Entry(row,font=('Georgia',15));name.grid(row=0,column=1,padx=10)
  self.label(row,'Age',14).grid(row=0,column=2,padx=15);age=tk.Spinbox(row,from_=10,to=120,width=6,font=('Georgia',14));age.grid(row=0,column=3)
  self.label(f,'CHOOSE YOUR CALLING',18).pack(pady=12)
  cls=tk.StringVar();grid=tk.Frame(f,bg=PARCH);grid.pack(pady=10)
  for j,(kind,desc) in enumerate([('Fighter','Steel & Resolve'),('Rogue','Shadow & Precision'),('Mage','Arcane Knowledge'),('Vessel','Spirit & Balance')]):
   area=tk.Frame(grid,bg='#bba278',highlightbackground=WOOD,highlightthickness=3);area.grid(row=0,column=j,padx=6)
   cv=tk.Canvas(area,width=132,height=155,bg='#686456',highlightthickness=0);cv.pack(padx=5,pady=6);art.character(cv,18,20,kind,j+15,4)
   self.button(area,kind,lambda kind=kind:cls.set(kind),True).pack(fill='x',padx=5)
   self.label(area,desc,10,bg='#bba278').pack(pady=8)
  chosen=self.label(f,'Select a class before binding your fate.',12);chosen.pack(pady=6);cls.trace_add('write',lambda *_:chosen.config(text='Selected: '+cls.get()))
  def roll():
   try:
    if not cls.get():raise ValueError('Select a class first.')
    if not messagebox.askyesno('Permanent roll','Generate this character permanently? There are no rerolls.'):return
    hero=game.character(name.get(),int(age.get()),cls.get());game.add_hero(self.c,hero);game.save(DATA,self.c);self._show()
   except ValueError as e:messagebox.showerror('Character',str(e))
  self.button(f,'BIND MY FATE  ·  PERMANENT ROLL',roll).pack(pady=15)
 def _start(self):game.start(self.c);story.ensure(self.c);game.save(DATA,self.c);self._adventure()
 def _scene(self,cv,place):
  if not cv.winfo_exists():return
  cv.delete('all');w=max(650,cv.winfo_width());h=max(270,cv.winfo_height());art.world(cv,place,self.c is not None and bool(self.c.get('enemy')),w,h)
  if self.c and self.c.get('enemy') and self.c.get('characters'):
   hero=self.c['characters'][self.c['active']]
   art.character(cv,round(w*.19),round(h*.47),hero['class'],hero['sprite_seed'],2)
   cv.create_text(round(w*.24),round(h*.9),text=hero['name']+'  HP '+str(hero['hp']),fill='#ffeac0',font=('Georgia',13,'bold'))
   enemy=self.c['enemy']
   # Placeholder opponent remains visible until approved animation pack is installed.
   art.character(cv,round(w*.7),round(h*.47),'Rogue',self.c['world_seed'],2)
   cv.create_text(round(w*.76),round(h*.9),text=enemy['name']+'  HP '+str(enemy['hp']),fill='#ffeac0',font=('Georgia',13,'bold'))
   if self.last_visual_cue:
    cv.create_text(round(w*.5),25,text=self.last_visual_cue.action.upper()+' · '+(self.last_visual_cue.effect or 'NO IMPACT'),fill='#ffda91',font=('Georgia',12,'bold'))
 def _switch(self,i):self.last_visual_cue=None;self.animation_director.clear();self.c['active']=i;game.save(DATA,self.c);self._adventure()
 def _adventure(self):
  self.page('The Hollow Bell')
  if not self.c['started']:
   outer,inside=self.card(self,'The party has gathered');outer.pack(fill='both',expand=True,padx=80,pady=25)
   for hero in self.c['characters']:self.label(inside,hero['name']+' · '+hero['class']+' · '+hero['path'],16).pack(padx=18,pady=10)
   self.button(inside,'BEGIN THE ADVENTURE',self._start).pack(pady=25)
   return
  body=tk.Frame(self,bg=DARK)
  body.pack(fill='both',expand=True,padx=14,pady=10)
  right=tk.Frame(body,bg=DARK,width=330)
  right.pack(side='right',fill='y',padx=(9,0))
  right.pack_propagate(False)
  self._sidebar(right)
  left=tk.Frame(body,bg=DARK)
  left.pack(side='left',fill='both',expand=True)
  party,party_inside=self.card(left,'Your party')
  party.pack(fill='x',pady=(0,7))
  members=tk.Frame(party_inside,bg=PARCH)
  members.pack(fill='x',padx=12,pady=7)
  for i,h in enumerate(self.c['characters']):
   line=('%s  ·  %s  ·  HP %s/%s'%(h['name'],game.display_archetype(h),h['hp'],h['max_hp']))
   self.button(members,('◆ ' if i==self.c['active'] else '')+line,lambda i=i:self._switch(i),True).pack(side='left',padx=3,pady=3)
  outer,f=self.card(left,story.PLACES[self.c['location']][0])
  outer.pack(fill='both',expand=True)
  cv=tk.Canvas(f,height=225,bg=DARK,highlightthickness=0)
  cv.pack(fill='x',padx=12,pady=8)
  cv.bind('<Configure>',lambda e:self._scene(cv,self.c['location']))
  self.label(f,story.journal(self.c),15,wraplength=650).pack(anchor='w',padx=18,pady=5)
  self.label(f,story.flavour(self.c,DATA),12,wraplength=650).pack(anchor='w',padx=18,pady=4)
  historybox=tk.Frame(f,bg='#f7e7c6',highlightbackground=BRASS,highlightthickness=1)
  historybox.pack(fill='both',expand=True,padx=14,pady=(6,9))
  history=tk.Text(historybox,font=('Georgia',12),bg='#f7e7c6',fg=INK,relief='flat',wrap='word',height=7,padx=10,pady=8)
  history.pack(side='left',fill='both',expand=True)
  scroll=tk.Scrollbar(historybox,command=history.yview)
  scroll.pack(side='right',fill='y')
  history.configure(yscrollcommand=scroll.set)
  lines=self.c['history'][-45:] or ['Your party arrives in Briarhollow.']
  history.insert('1.0','\\n\\n'.join(lines))
  history.configure(state='disabled')
  history.see('end')
  if self.c.get('enemy'):
   foe=self.c['enemy']
   battle=tk.Frame(f,bg='#513322',highlightbackground=BRASS,highlightthickness=2)
   battle.pack(fill='x',padx=14,pady=5)
   self.label(battle,f"⚔ BATTLE · {foe['name']} · HP {foe['hp']}/{foe.get('max_hp',foe['hp'])}",13,LIGHT,'#513322').pack(anchor='w',padx=10,pady=5)
   actions=tk.Frame(battle,bg='#513322');actions.pack(fill='x',padx=8,pady=4)
   for caption,command in [('ATTACK','I attack the enemy'),('GUARD','I guard'),('NEGOTIATE','I negotiate')]:
    self.button(actions,caption,lambda command=command:self._free(command),True).pack(side='left',padx=4)
  if self.busy:
   self.label(f,'The Dungeon Master is preparing the next passage...',11).pack(anchor='w',padx=16,pady=3)
  self.label(f,'WHAT DO YOU DO?',13).pack(anchor='w',padx=16,pady=(0,3))
  row=tk.Frame(f,bg=PARCH)
  row.pack(fill='x',padx=13,pady=(0,12))
  entry=tk.Entry(row,font=('Georgia',14),bg='#fff0d3',fg=INK,insertbackground=INK,relief='solid',bd=2)
  entry.pack(side='left',fill='x',expand=True,padx=4,ipady=6)
  def submit():
   entered=entry.get().strip()
   if entered:self._free(entered)
  entry.bind('<Return>',lambda event:submit())
  self.button(row,'SEND ACTION',submit,True).pack(side='right',padx=4)
  entry.focus_set()
 def _sidebar(self,parent):
  h=self.c['characters'][self.c['active']];outer,f=self.card(parent,'Adventurer’s Record');outer.pack(fill='both',expand=True)
  cv=tk.Canvas(f,width=245,height=182,bg='#9a9179',highlightthickness=0);cv.pack(pady=8);self._portrait(cv,h)
  self.label(f,h['name'],20).pack(padx=14)
  self.label(f,h['class']+' · '+game.display_archetype(h)+' · Level '+str(h['level']),12).pack(padx=14,pady=5)
  self.label(f,f'HEALTH  {h["hp"]}/{h["max_hp"]}      MANA  {h["mana"]}/{h["max_mana"]}',11).pack(padx=14,pady=6)
  row=tk.Frame(f,bg=PARCH);row.pack(fill='x',padx=8,pady=4)
  for i,name in enumerate(['Character Sheet','Inventory','Abilities','Journal','Story Tree','Shop','Map','Dice Board']):
   panel={'Character Sheet':'Record','Inventory':'Pack'}.get(name,name)
   self.button(row,name,lambda x=panel:self._panel(x),True).grid(row=i//2,column=i%2,padx=3,pady=3,sticky='ew')
  row.grid_columnconfigure(0,weight=1)
  row.grid_columnconfigure(1,weight=1)
  txt=tk.Frame(f,bg=PARCH);txt.pack(fill='both',expand=True,padx=16,pady=8)
  if self.panel=='Record':
   for k,v in h['stats'].items():self.label(txt,f'{k}      {v:>2}     ({(v-10)//2:+d})',13).pack(anchor='w',pady=2)
   self.label(txt,'Magic: '+h['magic'],12).pack(anchor='w',pady=6)
  elif self.panel=='Pack':
   for thing in h['inventory']:
    line=tk.Frame(txt,bg=PARCH);line.pack(fill='x',pady=2)
    self.label(line,'◇  '+thing,12).pack(side='left')
    if thing in ('Health Potion','Healing Draught'):
     self.button(line,'USE',lambda item=thing:self._consume(item),True).pack(side='right')
    elif thing in equipment.WEAPONS:
     suffix=' (equipped)' if equipment.equipped(h)==thing else ''
     if suffix:self.label(line,suffix,10).pack(side='left')
     self.button(line,'EQUIP',lambda item=thing:self._equip(item),True).pack(side='right')
   self.label(txt,f'Gold: {h["gold"]}',14).pack(anchor='w',pady=9)
  elif self.panel=='Abilities':
   for thing in h['moves']+h['passives']:self.label(txt,'◆  '+thing,12).pack(anchor='w',pady=5)
   if h['class']=='Mage' and h.get('magic') in spell_catalog.MAGIC_TYPES:
    unlocked=set(spell_catalog.unlocked(h['magic'],h['level']))
    for entry in spell_catalog.catalog(h['magic']):
     if entry['level']>1:
      label=('✦  ' if entry['name'] in unlocked else '◇  ')+entry['name']+'  ·  Level '+str(entry['level'])
      self.label(txt,label,11).pack(anchor='w',pady=2)
   elif h['class'] in ('Fighter','Rogue','Vessel'):
    unlocked=set(technique_catalog.unlocked(h['path'],h['level']))
    for entry in technique_catalog.catalog(h['path']):
     label=('✦  ' if entry['name'] in unlocked else '◇  ')+entry['name']+'  ·  Level '+str(entry['level'])
     self.label(txt,label,11).pack(anchor='w',pady=2)
  elif self.panel=='Shop':
   if not merchant.available(self.c):
    self.label(txt,"Visit Yarrow's Apothecary to trade. No trading during combat.",12,wraplength=260).pack(anchor='w',pady=8)
   else:
    self.label(txt,f"PURSE · {h['gold']} gold",14).pack(anchor='w',pady=6)
    for item,detail in merchant.CATALOG.items():
     line=tk.Frame(txt,bg=PARCH);line.pack(fill='x',pady=3)
     self.label(line,f"{item} · {detail['price']}g",10).pack(side='left')
     self.button(line,'BUY',lambda item=item:self._trade('buy',item),True).pack(side='right')
    self.label(txt,'SELL FROM PACK',12).pack(anchor='w',pady=6)
    for item in sorted(set(h['inventory'])):
     if item not in merchant.CATALOG:continue
     line=tk.Frame(txt,bg=PARCH);line.pack(fill='x',pady=2)
     self.label(line,item,10).pack(side='left')
     self.button(line,'SELL',lambda item=item:self._trade('sell',item),True).pack(side='right')
  elif self.panel=='Map':
   self._minimap(txt)
  elif self.panel=='Dice Board':
   records=dice_ledger.history(self.c)
   if not records:self.label(txt,'No dice rolled yet. Mundane actions do not need a roll.',11,wraplength=270).pack(anchor='w',pady=7)
   for record in reversed(records[-12:]):
    self.label(txt,f"D20 {record['roll']} {record['modifier']:+d} = {record['total']} / DC {record['dc']}",11).pack(anchor='w',pady=2)
  elif self.panel=='Story Tree':self.label(txt,story_tree.journal_text(self.c),12,wraplength=270).pack(anchor='w',pady=3)
  else:self.label(txt,story.journal(self.c),13,wraplength=270).pack(anchor='w')
 def _minimap(self,parent):
  """Interactive map mirrors quest routes; clicking is rules-gated."""
  state=atlas.state(self.c)
  canvas=tk.Canvas(parent,width=270,height=225,bg='#e8d5aa',highlightbackground=BRASS,highlightthickness=2)
  canvas.pack(pady=9)
  by_id={node['id']:node for node in state['nodes']}
  for start,end in state['roads']:
   a,b=by_id[start],by_id[end]
   canvas.create_line(a['x']*2.4,a['y']*2.0+10,b['x']*2.4,b['y']*2.0+10,fill='#987b56',width=3,dash=(5,3))
  for node in state['nodes']:
   x,y=node['x']*2.4,node['y']*2.0+10
   color='#486742' if node['current'] else '#8f653b' if node['reachable'] else '#aea18b'
   tag='place_'+node['id']
   canvas.create_oval(x-8,y-8,x+8,y+8,fill=color,outline=INK,tags=(tag,))
   canvas.create_text(x,y+16,text=node['label'],font=('Georgia',8),fill=INK,tags=(tag,))
   if node['reachable']:
    canvas.tag_bind(tag,'<ButtonRelease-1>',lambda event,dest=node['id']:self._map_travel(dest))
  self.label(parent,'Green: party location · Brown: available road',10,wraplength=260).pack(anchor='w')
 def _map_travel(self,destination):
  try:
   atlas.travel(self.c,destination)
   game.save(DATA,self.c)
   self._adventure()
  except ValueError as exc:messagebox.showwarning('Map',str(exc))
 def _trade(self,operation,item):
  try:
   if operation=='buy':merchant.buy(self.c,item)
   elif operation=='sell':merchant.sell(self.c,item)
   else:raise ValueError('Unknown trade action.')
   game.save(DATA,self.c)
   self._adventure()
  except ValueError as exc:messagebox.showwarning("Yarrow's Apothecary",str(exc))
 def _equip(self,item):
  try:
   equipment.equip(self.c,item)
   game.save(DATA,self.c)
   self._adventure()
  except ValueError as e:messagebox.showwarning('Equipment',str(e))
 def _consume(self,item):
  try:
   game.use_item(self.c,item)
   game.save(DATA,self.c)
   self._adventure()
  except ValueError as e:messagebox.showwarning('Inventory',str(e))
 def _panel(self,name):self.panel=name;self._adventure()
 def _choose(self,key):
  try:
   result=story.select(self.c,key);self.last_visual_cue=None;self.animation_director.clear();game.save(DATA,self.c)
   if key in ('attack','guard','negotiate'):self._narrate(result)
   self._adventure()
  except ValueError as e:messagebox.showwarning('Adventure',str(e))
 def _free(self,text):
  text=text.strip()
  if not text:return
  try:
   had_enemy=bool(self.c.get('enemy'))
   result=interaction.perform(self.c,text)
   hero=self.c['characters'][self.c['active']]
   if result['roll_required']:
    visual=visual_mapping.cue_for(hero,result)
    self.last_visual_cue=self.animation_director.enqueue(str(hero['id']),visual['animation'],visual['effect'] or '')
   else:
    self.last_visual_cue=None
    self.animation_director.clear()
   game.save(DATA,self.c)
   if had_enemy and self.c.get('enemy') is None and story.ensure(self.c)['stage']==3:
    story.ensure(self.c)['stage']=4;self.c['location']='square';game.save(DATA,self.c)
   if self.c.get('enemy') is None:self.last_visual_cue=None;self.animation_director.clear()
   self._adventure()
   if result['roll_required']:self._roll_display(result)
   self._narrate(result['result'])
  except ValueError as e:messagebox.showwarning('Action',str(e))
 def _roll_display(self,result):
  win=tk.Toplevel(self);win.title('The Fates Decide');win.geometry('400x350');win.configure(bg=WOOD)
  outer,f=self.card(win,'The Twenty-Sided Die');outer.pack(fill='both',expand=True,padx=16,pady=14)
  tray=tk.Canvas(f,width=285,height=145,bg='#5e4330',highlightthickness=3,highlightbackground=BRASS)
  tray.pack(pady=11)
  tray.create_rectangle(13,12,273,135,fill='#704c32',outline='#bd965d',width=5)
  tray.create_rectangle(26,24,260,122,fill='#3b6049',outline='#2a382f',width=3)
  tray.create_polygon(143,29,209,76,183,118,102,118,77,76,fill='#b99450',outline='#e9d09d',width=3)
  tray.create_polygon(143,29,143,76,77,76,fill='#d6b477',outline='#f5e0ad',width=2)
  tray.create_polygon(143,76,183,118,102,118,fill='#8e6435',outline='#edcd92',width=2)
  tray.create_text(143,80,text=str(result['roll']),fill='#fff2d5',font=('Georgia',32,'bold'))
  self.label(f,result['degree'],20).pack(pady=4)
  self.label(f,f'{result["roll"]} {result["modifier"]:+d} = {result["total"]}   ·   DC {result["dc"]}',13).pack(pady=5)
  self.button(f,'CONTINUE',win.destroy).pack(pady=10)
 def _narrate(self,resolved):
  if self.busy:return
  self.busy=True;identity=self.c['id'];snapshot=json.loads(json.dumps(self.c))
  def worker():
   try:message=ai.narrate(snapshot,resolved)
   except Exception:message='The Dungeon Master is unavailable. Your dice results and campaign remain saved.'
   self.q.put(('story',(identity,message)))
  threading.Thread(target=worker,daemon=True).start()
 def _generate_scene(self,popup,status):
  """Explicit opt-in ComfyUI generation; never run image models inside Tk."""
  place=self.c.get('location','square') if self.c else 'square'
  if popup.winfo_exists():status.config(text='ComfyUI: generating '+place+' artwork. This may take several minutes...')
  def worker():
   try:
    result=comfy_art.generate(place,DATA)
    self.q.put(('generated',(popup,status,place,str(result),None)))
   except Exception as e:
    self.q.put(('generated',(popup,status,place,None,str(e)[:200])))
  threading.Thread(target=worker,daemon=True).start()
 def _check_app_releases(self):
  """Check for a real released app without modifying the running Mac bundle."""
  def worker():
   result=app_release_checker.check('1.0.0')
   self.q.put(('app_release',result))
  threading.Thread(target=worker,daemon=True).start()

 def _rollback_content(self):
  """Restore the last verified content package, never edit saved adventures."""
  try:
   update_addons.rollback(DATA)
   self.update_status='Previous content restored; restart optional.'
   if self.c:self._adventure()
   else:self._home()
  except (ValueError,OSError,KeyError) as e:
   messagebox.showwarning('Content Recovery',str(e))

 def _check_content_updates(self):
  """Network and disk activity happen outside Tk's event loop."""
  def worker():
   result=addon_updates.check_and_install(DATA)
   self.q.put(('updates',result))
  threading.Thread(target=worker,daemon=True).start()
 def _poll(self):
  if self._closed:return
  try:
   while True:
    kind,value=self.q.get_nowait()
    if kind=='services':
     popup,label,result=value
     if popup.winfo_exists():
      label.config(text='\n'.join(k.title()+': '+v['message'] for k,v in result.items()))
    if kind=='generated':
     popup,label,place,path,error=value
     if popup.winfo_exists():
      label.config(text=('Illustration saved for '+place if path else 'ComfyUI: '+str(error)))
     if path:
      if self.c:self._adventure()
      else:self._home()
    if kind=='app_release':
     if value.get('status')=='available':
      self.update_status='Application '+value['version']+' available: '+value['download_url']
     elif value.get('status')=='current':self.update_status='Application release is current'
     else:self.update_status='No verified application release found'
     messagebox.showinfo('Application Releases',self.update_status+'\\nThe Mac app will not modify itself.')
    if kind=='updates':
     status,version=value
     self.update_status=('Art and stories updated to '+version if status=='updated' else
                         'Current: '+version if status=='current' else 'Offline / updates unavailable')
     if status=='updated':
      if self.c:self._adventure()
      else:self._home()
    if kind=='story':
     self.busy=False
     if self.c and self.c['id']==value[0]:
      self.c['history'].append('Dungeon Master: '+value[1]);game.save(DATA,self.c);self._adventure()
  except queue.Empty:pass
  if not self._closed:self._poll_job=self.after(400,self._poll)
 def destroy(self):
  self._closed=True
  if self._poll_job is not None:
   try:self.after_cancel(self._poll_job)
   except tk.TclError:pass
   self._poll_job=None
  super().destroy()
 def _exit(self):game.save(DATA,self.c);self._home()
if __name__=='__main__':App().mainloop()