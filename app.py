"""ACE Adventures 3 illustrated story-first native Tk interface."""
import json,queue,threading,tkinter as tk
from tkinter import messagebox
from pathlib import Path
import merchant,equipment,atlas,dice_ledger,loot_system,town_services,training_scrolls
import game,ai,story,art,ai_connections,addon_updates,update_addons,app_release_checker,comfy_art,asset_registry,story_tree,animation_director,visual_mapping,spell_catalog,technique_catalog,interaction,ability_progression
from io import BytesIO
import visual_theme,battle_effects,tabletop_layout,pixel_controls
DATA=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'
DARK=visual_theme.COLORS['background'];PARCH=visual_theme.COLORS['parchment'];INK=visual_theme.COLORS['ink'];BRASS=visual_theme.COLORS['brass'];WOOD=visual_theme.COLORS['wood'];LIGHT=visual_theme.COLORS['ivory']
class App(tk.Tk):
 def __init__(self):
  super().__init__();self.title('ACE Adventures III — The Hollow Bell');self.geometry('1300x880');self.minsize(960,700);self.configure(bg=DARK)
  self.c=None;self.busy=False;self.pending_narration=None;self.q=queue.Queue();self.panel='Record';self.last_roll=None;self.update_status='Not checked';self._sprite_refs=[];self.animation_director=animation_director.Director();self.last_visual_cue=None;self.last_visual_tier=1;self.asset_pack=asset_registry.Registry(asset_registry.find_approved_assets(DATA),max_cache_bytes=16*1024*1024);self._poll_job=None;self._closed=False;self._load_asset_index();self._home();self._poll_job=self.after(400,self._poll)
 def _load_asset_index(self):
  """Load artwork from a bundled approved pack or the user's installed pack."""
  index=self.asset_pack.root/'manifest.json'
  if index.is_file():
   try:self.asset_pack.load(index)
   except (OSError,ValueError):pass
 def _pixel_asset(self,canvas,category,tags,width,height,x=None,y=None):
  """Render a verified indexed PNG using crisp nearest-neighbor pixel scaling."""
  try:
   keys=self.asset_pack.choose(category,**tags)
   if not keys:return False
   from PIL import Image,ImageTk
   for key in keys:
    raw=self.asset_pack.bytes(key)
    if raw is None:continue
    with Image.open(BytesIO(raw)) as src:
     image=src.convert('RGBA')
     image.thumbnail((int(width),int(height)),Image.Resampling.NEAREST)
     photo=ImageTk.PhotoImage(image,master=canvas)
    canvas.create_image(x if x is not None else int(width)//2,
                        y if y is not None else int(height)//2,image=photo)
    canvas._ace_art_refs=getattr(canvas,'_ace_art_refs',[])+[photo]
    return True
  except (OSError,ValueError,ImportError,tk.TclError):pass
  return False
 def _item_art(self,parent,item):
  """Small approved sprite icon beside shop and inventory rows."""
  holder=tk.Canvas(parent,width=32,height=32,bg=PARCH,highlightthickness=0)
  if not self._pixel_asset(holder,'icon',{'item':item.lower().replace(' ','_')},28,28,16,16):
   holder.create_rectangle(4,4,28,28,outline=BRASS,width=2)
   holder.create_text(16,16,text='✦',font=('Georgia',14,'bold'),fill=WOOD)
  holder.pack(side='left',padx=(2,5))
  return holder
 def _portrait(self,canvas,hero):
  """Use the same approved portrait in full-size and compact sidebar mode."""
  width=int(canvas.cget('width'));height=int(canvas.cget('height'))
  compact=height<130
  key=asset_registry.select_character_sprite(self.asset_pack,hero,'portrait')
  if key is None:key=asset_registry.select_character_sprite(self.asset_pack,hero,'body')
  source=self.asset_pack.bytes(key) if key else None
  if source:
   try:
    from PIL import Image,ImageTk
    with Image.open(BytesIO(source)) as img:
     img=img.convert('RGBA')
     img.thumbnail((min(190,width-18),height-18),Image.Resampling.NEAREST)
     photo=ImageTk.PhotoImage(img.copy(),master=canvas)
    canvas.create_image(width//2,height//2,image=photo,anchor='center')
    canvas.create_rectangle(6,6,width-6,height-6,outline=BRASS,width=2)
    canvas.image=photo
    return
   except (ImportError,OSError,ValueError,tk.TclError):pass
  canvas.create_rectangle(6,6,width-6,height-6,outline=BRASS,width=2)
  scale=1 if compact else max(2,min(4,height//110))
  art.character(canvas,max(2,(width-32*scale)//2),max(2,(height-33*scale)//2),hero['class'],hero['sprite_seed'],scale)
 def _battle_character(self,canvas,hero,x,y,size):
  """Use approved body artwork in combat, preserving stable character identity."""
  key=asset_registry.select_character_sprite(self.asset_pack,hero,'body')
  if key is None:key=asset_registry.select_character_sprite(self.asset_pack,hero,'idle')
  content=self.asset_pack.bytes(key) if key else None
  if content:
   try:
    from PIL import Image,ImageTk
    with Image.open(BytesIO(content)) as raw:
     frame=raw.convert('RGBA')
     # Sheets store cells in the first frame; never display the entire atlas.
     if frame.width>=64 and frame.height>=64 and (frame.width>128 or frame.height>128):
      frame=frame.crop((0,0,64,64))
     frame.thumbnail((max(48,78*size),max(48,82*size)),Image.Resampling.NEAREST)
     photo=ImageTk.PhotoImage(frame,master=canvas)
    canvas.create_image(x,y,image=photo,anchor='center')
    canvas._ace_characters=getattr(canvas,'_ace_characters',[])+[photo]
    return True
   except (ImportError,OSError,ValueError,tk.TclError):pass
  art.character(canvas,x-14*size,y-14*size,hero['class'],hero['sprite_seed'],size)
  return False
 def clear(self):
  for widget in self.winfo_children():widget.destroy()
 def label(self,parent,text,size=12,fg=INK,bg=PARCH,**kw):
  return tk.Label(parent,text=text,font=('Georgia',size,'bold' if size>=17 else 'normal'),fg=fg,bg=bg,justify='left',wraplength=kw.get('wraplength',0),anchor='w')
 def button(self,parent,text,fn,light=False):
  """Use an approved image skin where available; callbacks remain real widgets."""
  lookup={'ATTACK':'attack','MAGIC':'magic','BUY':'buy','SELL':'sell',
          'EQUIP':'equip'}
  asset=None
  match=lookup.get(text.strip().upper())
  if match:
   keys=self.asset_pack.choose('icon',ui=match)
   if keys:asset=self.asset_pack.bytes(keys[0])
  return pixel_controls.PixelButton(parent,text,fn,light,artwork=asset)

 def page(self,title):
  self.clear();bar=tk.Frame(self,bg=visual_theme.COLORS['wood_dark'],height=72);bar.pack(fill='x')
  self.label(bar,'A.C.E.  ADVENTURES III    ✦',22,LIGHT,visual_theme.COLORS['wood_dark']).pack(side='left',padx=20,pady=12)
  self.label(bar,'❦  '+title.upper(),11,BRASS,visual_theme.COLORS['wood_dark']).pack(side='left',padx=14)
  self.button(bar,'THE CHRONICLES',self._home).pack(side='right',padx=12)
  self.button(bar,'AI CONNECTIONS',self._connections).pack(side='right',padx=5)
  self.button(bar,'CHECK UPDATES',self._check_content_updates).pack(side='right',padx=5)
 def card(self,parent,title=''):
  outer=tk.Frame(parent,bg=visual_theme.COLORS['wood_dark'],bd=4,relief='flat',highlightbackground=BRASS,highlightthickness=2)
  inner=tk.Frame(outer,bg=PARCH,highlightbackground=visual_theme.COLORS['wood_highlight'],highlightthickness=4)
  inner.pack(fill='both',expand=True,padx=5,pady=5)
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
  self.pending_narration=None
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
  cv.delete('all');cv._ace_characters=[];cv._ace_art_refs=[];w=max(10,cv.winfo_width());h=max(10,cv.winfo_height());
  if not self._pixel_asset(cv,'background',{'place':str(place).lower()},w,h,w//2,h//2):art.world(cv,place,self.c is not None and bool(self.c.get('enemy')),w,h)
  if self.c and self.c.get('enemy') and self.c.get('characters'):
   hero=self.c['characters'][self.c['active']]
   size=max(1,min(3,int(h/120)))
   cv.create_oval(round(w*.08),round(h*.78),round(w*.34),round(h*.84),fill='#403c35',outline='#c5a16e',width=2)
   self._battle_character(cv,hero,round(w*.21),round(h*.55),size)
   cv.create_text(round(w*.24),round(h*.9),text=hero['name']+'  HP '+str(hero['hp']),fill='#ffeac0',font=('Georgia',13,'bold'))
   enemy=self.c['enemy']
   cv.create_oval(round(w*.67),round(h*.79),round(w*.91),round(h*.85),fill='#403c35',outline='#c5a16e',width=2)
   if not self._pixel_asset(cv,'body',{'enemy':str(enemy['name']).lower().replace(' ','_')},min(180,int(w*.32)),min(180,int(h*.65)),round(w*.78),round(h*.55)):
    art.enemy(cv,round(w*.78),round(h*.55),enemy['name'],self.c['world_seed'],size)
   cv.create_text(round(w*.75),round(h*.92),text=enemy['name']+'  HP '+str(enemy['hp']),fill='#ffeac0',font=('Georgia',12,'bold'))
   if self.last_visual_cue:
    effect=self.last_visual_cue.effect
    if effect:
     battle_effects.paint(cv,effect,round(w*.52),round(h*.49),getattr(self,'last_visual_tier',1))
    elif self.last_visual_cue.action=='guard':
     cv.create_oval(round(w*.12),round(h*.22),round(w*.32),round(h*.8),outline='#9ad1c2',width=4)
    elif self.last_visual_cue.action=='attack':
     cv.create_line(round(w*.30),round(h*.58),round(w*.68),round(h*.58),fill='#f0ce83',width=4,dash=(7,7))
    cv.create_text(round(w*.5),25,text=self.last_visual_cue.action.upper()+' · '+(self.last_visual_cue.effect or 'NO IMPACT'),fill='#ffda91',font=('Georgia',12,'bold'))
 def _switch(self,i):self.last_visual_cue=None;self.animation_director.clear();self.c['active']=i;game.save(DATA,self.c);self._adventure()
 def _adventure(self):
  self.page('The Hollow Bell')
  if not self.c['started']:
   outer,inside=self.card(self,'The party has gathered');outer.pack(fill='both',expand=True,padx=80,pady=25)
   for hero in self.c['characters']:self.label(inside,hero['name']+' · '+hero['class']+' · '+hero['path'],16).pack(padx=18,pady=10)
   self.button(inside,'BEGIN THE ADVENTURE',self._start).pack(pady=25)
   return
  layout=tabletop_layout.for_window(self.winfo_width(),self.winfo_height(),len(self.c['characters']),in_battle=bool(self.c.get('enemy')))
  body=tk.Frame(self,bg=DARK)
  body.pack(fill='both',expand=True,padx=14,pady=10)
  right=tk.Frame(body,bg=DARK,width=layout.sidebar)
  right.pack(side='right',fill='y',padx=(9,0))
  right.pack_propagate(False)
  self._sidebar(right)
  # Match the original concept's permanent left-hand party roster.
  party_column=tk.Frame(body,bg=DARK,width=195)
  party_column.pack(side='left',fill='y',padx=(0,8))
  party_column.pack_propagate(False)
  left=tk.Frame(body,bg=DARK)
  left.pack(side='left',fill='both',expand=True)
  party,party_inside=self.card(party_column,'Your party')
  party.pack(fill='both',expand=True,pady=(0,7))
  members=tk.Frame(party_inside,bg=PARCH)
  members.pack(fill='both',expand=True,padx=3,pady=6)
  members.grid_columnconfigure(0,weight=1)
  for i,h in enumerate(self.c['characters']):
   selected=i==self.c['active']
   hero_frame=tk.Frame(members,bg=visual_theme.COLORS['parchment_light'] if selected else PARCH,
                       highlightbackground=BRASS if selected else visual_theme.COLORS['parchment_shadow'],
                       highlightthickness=2 if selected else 1)
   hero_frame.grid(row=i,column=0,sticky='ew',padx=1,pady=3)
   portrait=tk.Canvas(hero_frame,width=56,height=56,bg=visual_theme.COLORS['parchment_shadow'],highlightthickness=1,highlightbackground=BRASS)
   portrait.pack(side='left',padx=2,pady=3)
   self._portrait(portrait,h)
   title=('◆ ' if selected else '◇ ')+h['name']+' · Lv '+str(h['level'])
   self.button(hero_frame,title,lambda i=i:self._switch(i),True).pack(fill='x',padx=1,pady=(3,0))
   self.label(hero_frame,game.display_archetype(h),9,bg=hero_frame['bg']).pack(anchor='w',padx=4,pady=1)
   self.label(hero_frame,'HP '+str(h['hp'])+'/'+str(h['max_hp'])+' · MP '+str(h['mana'])+'/'+str(h['max_mana']),9,bg=hero_frame['bg']).pack(anchor='w',padx=4,pady=(0,1))
   bars=tk.Canvas(hero_frame,height=9,width=175,bg=hero_frame['bg'],highlightthickness=0)
   bars.pack(fill='x',padx=8,pady=(0,4))
   bar_width=140
   visual_theme.meter(bars,h['hp'],h['max_hp'],width=bar_width,height=8,fill=visual_theme.COLORS['forest'] if h['hp']>0 else visual_theme.COLORS['danger'])
   if h['hp']<=0:self.label(hero_frame,'INCAPACITATED',9,fg=visual_theme.COLORS['danger'],bg=hero_frame['bg']).pack(anchor='w',padx=8,pady=(0,3))
  outer,f=self.card(left,story.PLACES[self.c['location']][0])
  outer.pack(fill='both',expand=True)
  if self.busy:
   self.label(f,'The Dungeon Master is preparing the next passage...',11).pack(side='bottom',anchor='w',padx=16,pady=3)
  self.label(f,'WHAT DO YOU DO?',13).pack(side='bottom',anchor='w',padx=16,pady=(0,3))
  row=tk.Frame(f,bg=PARCH)
  row.pack(side='bottom',fill='x',padx=13,pady=(0,12))
  entry=tk.Entry(row,font=('Georgia',14),bg='#fff0d3',fg=INK,insertbackground=INK,relief='solid',bd=2)
  entry.pack(side='left',fill='x',expand=True,padx=4,ipady=6)
  def submit():
   entered=entry.get().strip()
   if entered:self._free(entered)
  entry.bind('<Return>',lambda event:submit())
  self.button(row,'SEND ACTION',submit,True).pack(side='right',padx=4)
  entry.focus_set()
  self.label(f,tabletop_layout.scene_caption(story.PLACES[self.c['location']][0],self.c.get('enemy')),11,fg=visual_theme.COLORS['muted_ink']).pack(anchor='w',padx=18,pady=(4,0))
  cv=tk.Canvas(f,height=layout.scene_height,bg=DARK,highlightthickness=0)
  cv.pack(fill='x',padx=12,pady=8)
  cv.bind('<Configure>',lambda e:self._scene(cv,self.c['location']))
  self.label(f,story.journal(self.c),15,wraplength=650).pack(anchor='w',padx=18,pady=5)
  self.label(f,story.flavour(self.c,DATA),12,wraplength=650).pack(anchor='w',padx=18,pady=4)
  historybox=tk.Frame(f,bg=visual_theme.COLORS['parchment_light'],highlightbackground=BRASS,highlightthickness=1)
  historybox.pack(fill='both',expand=not bool(self.c.get('enemy')),padx=14,pady=(6,6))
  history=tk.Text(historybox,font=('Georgia',12),bg=visual_theme.COLORS['parchment_light'],fg=INK,relief='flat',wrap='word',height=3 if self.c.get('enemy') else 7,padx=10,pady=8)
  history.pack(side='left',fill='both',expand=True)
  scroll=tk.Scrollbar(historybox,command=history.yview)
  scroll.pack(side='right',fill='y')
  history.configure(yscrollcommand=scroll.set)
  lines=self.c['history'][-45:] or ['Your party arrives in Briarhollow.']
  history.insert('1.0','\\n\\n'.join(lines))
  history.configure(state='disabled')
  history.see('end')
  if self.panel=='Dice Board' or (self.c.get('enemy') and dice_ledger.history(self.c)):
   self._dice_tray(f)
  if self.c.get('enemy'):
   foe=self.c['enemy']
   battle=tk.Frame(f,bg=WOOD,highlightbackground=BRASS,highlightthickness=2)
   battle.pack(fill='x',padx=14,pady=5,before=historybox)
   self.label(battle,'⚔  ENCOUNTER  ·  '+foe['name'].upper(),13,LIGHT,WOOD).pack(anchor='w',padx=10,pady=(7,2))
   phase=(' · PHASE '+str(foe.get('phase',1))) if foe.get('boss') else ''
   self.label(battle,'ENEMY HEALTH  '+str(foe['hp'])+'/'+str(foe.get('max_hp',foe['hp']))+phase,10,LIGHT,WOOD).pack(anchor='w',padx=10,pady=2)
   meter_canvas=tk.Canvas(battle,width=320,height=14,bg=WOOD,highlightthickness=0)
   meter_canvas.pack(anchor='w',padx=10,pady=(0,5))
   visual_theme.meter(meter_canvas,foe['hp'],foe.get('max_hp',foe['hp']),width=320,fill=visual_theme.COLORS['danger'])
   hero=self.c['characters'][self.c['active']]
   self.label(battle,'ACTIVE HERO  ·  '+hero['name']+'  ·  HP '+str(hero['hp'])+'/'+str(hero['max_hp'])+'  ·  MP '+str(hero['mana'])+'/'+str(hero['max_mana']),10,LIGHT,WOOD).pack(anchor='w',padx=10,pady=3)
   recent=dice_ledger.history(self.c)
   if recent:
    last=recent[-1]
    self.label(battle,'LAST ROLL   D20 '+str(last['roll'])+'  '+f"{last['modifier']:+d}"+' = '+str(last['total'])+' / DC '+str(last['dc']),10,visual_theme.COLORS['brass_light'],WOOD).pack(anchor='w',padx=10,pady=3)
   actions=tk.Frame(battle,bg=WOOD);actions.pack(fill='x',padx=8,pady=(5,8))
   if self.c.get('party_defeated'):
    self.button(actions,'RECOVER IN TOWN',lambda:self._free('recover party'),True).pack(side='left',padx=4)
   else:
    for caption,command in [('ATTACK','I attack the enemy'),('GUARD','I guard'),('NEGOTIATE','I negotiate')]:
     self.button(actions,caption,lambda command=command:self._free(command),True).pack(side='left',padx=4)
    self.button(actions,'ABILITIES',lambda:self._panel('Abilities'),True).pack(side='left',padx=4)
    self.button(actions,'POTIONS',lambda:self._panel('Pack'),True).pack(side='left',padx=4)

 def _dice_tray(self,parent):
  """Visualize rules-engine dice ledger, never generate a roll on display."""
  recent=dice_ledger.history(self.c)
  tray=tk.Frame(parent,bg=visual_theme.COLORS['wood_dark'],highlightbackground=BRASS,highlightthickness=2)
  tray.pack(fill='x',padx=14,pady=(5,3))
  self.label(tray,'DICE TRAY  ·  RESULTS FROM GAME RULES',10,LIGHT,visual_theme.COLORS['wood_dark']).pack(anchor='w',padx=8,pady=(4,0))
  display=tk.Canvas(tray,height=64,bg=visual_theme.COLORS['wood_dark'],highlightthickness=0)
  display.pack(fill='x',padx=6,pady=(0,5))
  w=340;cy=32
  if recent:
   row=recent[-1];v=int(row['roll']);modifier=int(row['modifier']);total=int(row['total'])
   vertices=[(40,5),(64,22),(57,48),(23,48),(16,22)]
   display.create_polygon(vertices,fill='#963e31',outline=visual_theme.COLORS['brass_light'],width=3)
   display.create_text(40,29,text=str(v),fill=LIGHT,font=('Georgia',17,'bold'))
   display.create_text(90,30,text=f'{modifier:+d}   =   {total}    (DC {row["dc"]})',anchor='w',fill=LIGHT,font=('Georgia',13,'bold'))
  else:
   display.create_text(15,30,text='Dice remain in the tray until an action requires a roll.',anchor='w',fill=LIGHT,font=('Georgia',11))
  return tray
 def _resource_bar(self,parent,label,current,maximum,color):
  frame=tk.Frame(parent,bg=PARCH);frame.pack(fill='x',padx=15,pady=(2,3))
  self.label(frame,f'{label}  {current}/{maximum}',10).pack(anchor='w')
  cv=tk.Canvas(frame,width=245,height=14,bg=PARCH,highlightthickness=0)
  cv.pack(anchor='w',fill='x',pady=(2,1))
  visual_theme.meter(cv,current,maximum,width=245,height=12,fill=color)
  return cv
 def _bind_ledger_scroll(self,viewport,root):
  """Scroll long sidebars with the wheel or trackpad without scrolling the whole UI."""
  def move(event):
   amount=-1 if event.delta>0 else 1 if event.delta<0 else 0
   if amount:viewport.yview_scroll(amount,'units')
   return 'break'
  def linux(direction):
   def fn(event):
    viewport.yview_scroll(direction,'units')
    return 'break'
   return fn
  def walk(widget):
   widget.bind('<MouseWheel>',move,add='+')
   widget.bind('<Button-4>',linux(-1),add='+')
   widget.bind('<Button-5>',linux(1),add='+')
   for child in widget.winfo_children():walk(child)
  walk(root)
  viewport.bind('<MouseWheel>',move,add='+')
  viewport.bind('<Button-4>',linux(-1),add='+')
  viewport.bind('<Button-5>',linux(1),add='+')
 def _sidebar(self,parent):
  h=self.c['characters'][self.c['active']];outer,f=self.card(parent,'Adventurer’s Record');outer.pack(fill='both',expand=True)
  if self.panel=='Record':
   cv=tk.Canvas(f,width=245,height=182,bg=visual_theme.COLORS['parchment_shadow'],highlightthickness=1,highlightbackground=BRASS)
   cv.pack(pady=8);self._portrait(cv,h)
   self.label(f,h['name'],20).pack(padx=14)
   self.label(f,h['class']+' · '+game.display_archetype(h)+' · Level '+str(h['level']),12).pack(padx=14,pady=5)
   self._resource_bar(f,'HEALTH',h['hp'],h['max_hp'],visual_theme.COLORS['forest'])
   self._resource_bar(f,'MANA',h['mana'],h['max_mana'],visual_theme.COLORS['mana'])
  else:
   self.label(f,h['name']+' · Lv '+str(h['level'])+' · '+game.display_archetype(h),12).pack(anchor='w',padx=14,pady=(5,2))
   self.label(f,'HEALTH '+str(h['hp'])+'/'+str(h['max_hp'])+' · MANA '+str(h['mana'])+'/'+str(h['max_mana']),10).pack(anchor='w',padx=14,pady=(0,4))
  row=tk.Frame(f,bg=PARCH);row.pack(fill='x',padx=8,pady=4)
  for i,name in enumerate(visual_theme.NAVIGATION):
   panel={'Character Sheet':'Record','Inventory':'Pack'}.get(name,name)
   nav=self.button(row,('◆ ' if self.panel==panel else '')+name,lambda x=panel:self._panel(x),True)
   nav.configure(padx=5,pady=4,font=('Georgia',9,'bold'))
   nav.grid(row=i//2,column=i%2,padx=2,pady=2,sticky='ew')
  row.grid_columnconfigure(0,weight=1)
  row.grid_columnconfigure(1,weight=1)
  ledger=tk.Frame(f,bg=PARCH)
  ledger.pack(fill='both',expand=True,padx=(10,4),pady=(4,8))
  viewport=tk.Canvas(ledger,bg=PARCH,highlightthickness=0,width=280,height=250)
  scrollbar=tk.Scrollbar(ledger,orient='vertical',command=viewport.yview)
  scrollbar.pack(side='right',fill='y')
  viewport.pack(side='left',fill='both',expand=True)
  viewport.configure(yscrollcommand=scrollbar.set)
  txt=tk.Frame(viewport,bg=PARCH)
  window_id=viewport.create_window((0,0),window=txt,anchor='nw')
  txt.bind('<Configure>',lambda event:viewport.configure(scrollregion=viewport.bbox('all')))
  viewport.bind('<Configure>',lambda event:viewport.itemconfigure(window_id,width=event.width))
  if self.panel=='Record':
   self.label(txt,'CHARACTER PROFILE',13).pack(anchor='w',pady=(0,8))
   self.label(txt,'Path  ·  '+h['path'],11).pack(anchor='w',pady=3)
   self.label(txt,'Magic ·  '+h['magic'],11).pack(anchor='w',pady=3)
   self.label(txt,'Level '+str(h['level'])+'  ·  XP '+str(h['xp']),11).pack(anchor='w',pady=3)
   self.label(txt,'ATTRIBUTES',13).pack(anchor='w',pady=(12,6))
   for k,v in h['stats'].items():
    self.label(txt,f'{k}       {v:>2}    ({(v-10)//2:+d})',12).pack(anchor='w',pady=3)
   self.label(txt,'EQUIPMENT',13).pack(anchor='w',pady=(12,6))
   weapon=equipment.equipped(h) or h.get('gear_slots',{}).get('weapon') or 'Unarmed'
   self.label(txt,'Weapon · '+weapon,11,wraplength=260).pack(anchor='w',pady=2)
   for slot in ('armor','trinket'):
    self.label(txt,slot.title()+' · '+h.get('gear_slots',{}).get(slot,'None'),11,wraplength=260).pack(anchor='w',pady=2)
  elif self.panel=='Pack':
   self.label(txt,'ADVENTURER’S PACK',13).pack(anchor='w',pady=(0,5))
   self.label(txt,'Gold · '+str(h['gold']),12).pack(anchor='w',pady=(0,8))
   for thing in h['inventory']:
    line=tk.Frame(txt,bg=PARCH);line.pack(fill='x',pady=2)
    status=' · EQUIPPED' if thing==equipment.equipped(h) or thing in h.get('gear_slots',{}).values() else ''
    self._item_art(line,thing)
    self.label(line,'◇  '+thing+status,10,wraplength=175).pack(side='left')
    if thing in ('Health Potion','Healing Draught'):
     self.button(line,'USE',lambda item=thing:self._consume(item),True).pack(side='right')
    elif thing in training_scrolls.SCROLLS:
     self.button(line,'STUDY',lambda item=thing:self._free('study '+item),True).pack(side='right')
    elif thing in loot_system.ITEMS:
     self.button(line,'EQUIP',lambda item=thing:self._free('equip '+item),True).pack(side='right')
    elif thing in equipment.WEAPONS:
     suffix=' (equipped)' if equipment.equipped(h)==thing else ''
     if suffix:self.label(line,suffix,10).pack(side='left')
     self.button(line,'EQUIP',lambda item=thing:self._equip(item),True).pack(side='right')
   self.label(txt,'Items · '+str(len(h['inventory'])),11).pack(anchor='w',pady=9)
  elif self.panel=='Abilities':
   self.label(txt,'AVAILABLE ACTIONS',12).pack(anchor='w',pady=4)
   for thing in h['moves']:
    ability_row=tk.Frame(txt,bg=PARCH);ability_row.pack(fill='x',pady=2)
    self.label(ability_row,'◆  '+ability_progression.display_name(h,thing),11).pack(side='left')
    self.button(ability_row,'USE',lambda move=thing:self._free('I use '+move),True).pack(side='right')
   for passive in h['passives']:
    self.label(txt,'◇  '+passive+' (passive)',10).pack(anchor='w',pady=2)
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
    last_category=None
    for item,detail in merchant.CATALOG.items():
     category=loot_system.ITEMS[item]['kind'].upper() if item in loot_system.ITEMS else 'SUPPLIES & SCROLLS'
     if category!=last_category:
      self.label(txt,category,12).pack(anchor='w',pady=(9,4))
      last_category=category
     line=tk.Frame(txt,bg=PARCH);line.pack(fill='x',pady=3)
     self._item_art(line,item)
     self.label(line,f"{item} · {detail['price']}g",10,wraplength=175).pack(side='left')
     self.button(line,'BUY',lambda item=item:self._trade('buy',item),True).pack(side='right')
    self.label(txt,'SELL FROM PACK',12).pack(anchor='w',pady=6)
    for item in sorted(set(h['inventory'])):
     if item not in merchant.CATALOG:continue
     line=tk.Frame(txt,bg=PARCH);line.pack(fill='x',pady=2)
     self._item_art(line,item)
     self.label(line,item,10).pack(side='left')
     self.button(line,'SELL',lambda item=item:self._trade('sell',item),True).pack(side='right')
  elif self.panel=='Town':
   quests=town_services.quest_status(self.c)
   self.label(txt,'ACTIVE QUESTS '+str(len(quests))+'/2',13).pack(anchor='w',pady=4)
   for quest in quests:
    self.label(txt,'◇ '+quest['name'],10).pack(anchor='w',pady=2)
    if quest.get('objective'):
     self.label(txt,'   ↳ '+quest['objective'],10).pack(anchor='w',pady=1)
   if self.c.get('last_enchant_spin'):
    spin=self.c['last_enchant_spin']
    self.label(txt,'LAST ENCHANT WHEEL: '+spin['outcome']+' +'+str(spin['level']),10).pack(anchor='w',pady=4)
   self.label(txt,'LOCAL PEOPLE',13).pack(anchor='w',pady=4)
   present=[name for name,info in town_services.PEOPLE.items() if info['place']==self.c['location']]
   for name in present:
    line=tk.Frame(txt,bg=PARCH);line.pack(fill='x',pady=2)
    self.label(line,name,10).pack(side='left')
    self.button(line,'TALK',lambda who=name:self._free('talk to '+who),True).pack(side='right')
   if self.c['location']=='square':
    self.label(txt,'ADVENTURERS GUILD · '+town_services.guild_rank(self.c),12).pack(anchor='w',pady=7)
    for name in town_services.available_jobs(self.c):
     self.button(txt,name,lambda job=name:self._free('accept guild job '+job),True).pack(fill='x',pady=2)
   if self.c.get('guild_job'):
    self.button(txt,'ABANDON GUILD JOB',lambda:self._free('abandon guild job'),True).pack(fill='x',pady=3)
    self.button(txt,'CLAIM GUILD REWARD',lambda:self._free('claim guild reward'),True).pack(fill='x',pady=5)
   if self.c['location']=='market':
    self.label(txt,'ENCHANT EQUIPMENT',12).pack(anchor='w',pady=5)
    for thing in sorted(set(h['inventory'])):
     if thing in loot_system.ITEMS:
      self.button(txt,'ENCHANT '+thing,lambda item=thing:self._free('enchant '+item),True).pack(fill='x',pady=2)
  elif self.panel=='Map':
   self.label(txt,'PARCHMENT ATLAS',13).pack(anchor='w',pady=(0,5))
   self._minimap(txt)
  elif self.panel=='Dice Board':
   records=dice_ledger.history(self.c)
   self.label(txt,'THE FATES · D20 LEDGER',13).pack(anchor='w',pady=(2,8))
   self.label(txt,'Only uncertain actions require a die roll.',10,wraplength=260).pack(anchor='w',pady=(0,7))
   if not records:self.label(txt,'No dice rolled yet.',11).pack(anchor='w',pady=7)
   for record in reversed(records[-20:]):
    line=tk.Frame(txt,bg=visual_theme.COLORS['parchment_light'],highlightbackground=BRASS,highlightthickness=1)
    line.pack(fill='x',pady=3)
    self.label(line,'D20  '+str(record['roll'])+'  '+f"{record['modifier']:+d}"+'  = '+str(record['total']),12,bg=visual_theme.COLORS['parchment_light']).pack(anchor='w',padx=8,pady=(5,0))
    self.label(line,'DC '+str(record['dc'])+'  ·  '+str(record.get('degree','')),10,bg=visual_theme.COLORS['parchment_light'],wraplength=245).pack(anchor='w',padx=8,pady=(0,5))
  elif self.panel=='Story Tree':
   self.label(txt,'THE HOLLOW BELL · CHRONICLE',13).pack(anchor='w',pady=(2,8))
   for i,step in enumerate(story_tree.timeline(self.c)):
    row=tk.Frame(txt,bg=visual_theme.COLORS['parchment_light'],highlightbackground=BRASS,highlightthickness=1)
    row.pack(fill='x',pady=3)
    marker='✓' if step['status']=='completed' else '◉' if step['status']=='current' else '◇'
    color=visual_theme.COLORS['forest'] if step['status']=='completed' else INK if step['status']=='current' else visual_theme.COLORS['muted_ink']
    self.label(row,marker+'  '+step['title'],10,fg=color,bg=visual_theme.COLORS['parchment_light'],wraplength=220).pack(anchor='w',padx=8,pady=7)
    if i<len(story_tree.STEPS)-1:
     self.label(txt,'    │',10,fg=BRASS).pack(anchor='w')
  elif self.panel=='Journal':
   self.label(txt,'CHRONICLE · QUEST JOURNAL',13).pack(anchor='w',pady=(2,7))
   self.label(txt,story.journal(self.c),12,wraplength=250).pack(anchor='w',pady=3)
   self.label(txt,'RECENT EVENTS',12).pack(anchor='w',pady=(13,6))
   for event in reversed(self.c.get('history',[])[-16:]):
    row=tk.Frame(txt,bg=visual_theme.COLORS['parchment_light'],highlightbackground=visual_theme.COLORS['parchment_shadow'],highlightthickness=1)
    row.pack(fill='x',pady=3)
    self.label(row,str(event)[:220],10,bg=visual_theme.COLORS['parchment_light'],wraplength=245).pack(anchor='w',padx=8,pady=5)
  else:self.label(txt,story.journal(self.c),13,wraplength=270).pack(anchor='w')
  self._bind_ledger_scroll(viewport,txt)
 def _minimap(self,parent):
  """Parchment cartography; destination clicks remain rules-gated."""
  state=atlas.state(self.c)
  canvas=tk.Canvas(parent,width=274,height=215,bg=visual_theme.COLORS['parchment_light'],
                   highlightbackground=BRASS,highlightthickness=2)
  canvas.pack(pady=9)
  canvas.create_rectangle(8,8,262,205,outline=BRASS,width=2)
  canvas.create_text(137,20,text='BRIARHOLLOW & ASHWOOD',font=('Georgia',10,'bold'),fill=INK)
  canvas.create_line(236,39,236,67,fill=visual_theme.COLORS['wood'],width=2)
  canvas.create_polygon(236,34,229,45,243,45,fill=visual_theme.COLORS['wood'])
  canvas.create_text(236,75,text='N',font=('Georgia',9,'bold'),fill=INK)
  coords={'square':(131,172),'tavern':(61,124),'market':(214,125),
          'well':(128,95),'forest':(158,51)}
  nodes={node['id']:node for node in state['nodes']}
  for a,b in state['roads']:
   xa,ya=coords[a];xb,yb=coords[b]
   canvas.create_line(xa,ya,xb,yb,fill='#b3996b',width=5)
   canvas.create_line(xa,ya,xb,yb,fill='#f4e5c4',width=2,dash=(5,4))
  for node in state['nodes']:
   key=node['id'];x,y=coords[key]
   color=(visual_theme.COLORS['forest'] if node['current']
          else visual_theme.COLORS['wood'] if node['reachable']
          else '#a8a096')
   tag='place_'+key
   radius=10 if node['current'] else 8
   canvas.create_oval(x-radius,y-radius,x+radius,y+radius,fill=color,
                      outline=BRASS,width=2,tags=(tag,))
   canvas.create_text(x,y-20 if key=='forest' else y+20,
                      text={'square':'VILLAGE SQUARE','tavern':'TAVERN','market':'APOTHECARY',
                            'well':'OLD WELL','forest':'ASHWOOD'}[key],
                      font=('Georgia',8,'bold'),fill=INK,tags=(tag,))
   if node['reachable']:
    canvas.tag_bind(tag,'<ButtonRelease-1>',lambda event,dest=key:self._map_travel(dest))
  self.label(parent,'Green: current place · Brown: available road',10,wraplength=260).pack(anchor='w')
  self.label(parent,'Select a marked destination to travel.',10,wraplength=260).pack(anchor='w',pady=(3,0))
 def _map_travel(self,destination):
  try:
   result=atlas.travel(self.c,destination)
   game.save(DATA,self.c)
   self._adventure()
   self._narrate(result)
  except ValueError as exc:messagebox.showwarning('Map',str(exc))
 def _trade(self,operation,item):
  try:
   if operation=='buy':result=merchant.buy(self.c,item)
   elif operation=='sell':result=merchant.sell(self.c,item)
   else:raise ValueError('Unknown trade action.')
   game.save(DATA,self.c)
   self._adventure()
   self._narrate(result)
  except ValueError as exc:messagebox.showwarning("Yarrow's Apothecary",str(exc))
 def _equip(self,item):
  try:
   result=equipment.equip(self.c,item)
   game.save(DATA,self.c)
   self._adventure()
   self._narrate(result)
  except ValueError as e:messagebox.showwarning('Equipment',str(e))
 def _consume(self,item):
  try:
   result=game.use_item(self.c,item)
   game.save(DATA,self.c)
   self._adventure()
   self._narrate(result)
  except ValueError as e:messagebox.showwarning('Inventory',str(e))
 def _panel(self,name):self.panel=name;self._adventure()
 def _choose(self,key):
  if key in ('attack','guard','negotiate'):
   self._free({'attack':'I attack the enemy','guard':'I guard','negotiate':'I negotiate'}[key])
   return
  try:
   result=story.select(self.c,key);self.last_visual_cue=None;self.animation_director.clear();game.save(DATA,self.c)
   self._adventure()
   self._narrate(result)
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
    self.last_visual_tier=visual.get('tier',1)
    self.last_visual_cue=self.animation_director.enqueue(str(hero['id']),visual['animation'],visual['effect'] or '')
   else:
    self.last_visual_cue=None
    self.animation_director.clear()
   game.save(DATA,self.c)
   if self.c.get('enemy') is None:self.last_visual_cue=None;self.animation_director.clear()
   self._adventure()
   if result.get('choice')=='enchant':self._enchant_wheel()
   if result['roll_required']:self._roll_display(result)
   self._narrate(result['result'])
  except ValueError as e:messagebox.showwarning('Action',str(e))
 def _enchant_wheel(self):
  spin=self.c.get('last_enchant_spin')
  if not spin:return
  win=tk.Toplevel(self);win.title('Enchantment Wheel');win.geometry('450x380');win.configure(bg=WOOD)
  outer,inner=self.card(win,'Wheel of Enchantments');outer.pack(fill='both',expand=True,padx=12,pady=12)
  cv=tk.Canvas(inner,width=330,height=250,bg=PARCH,highlightthickness=0);cv.pack()
  import math
  kinds=loot_system.ENCHANT_TYPES
  cx,cy=165,115
  cv.create_oval(cx-104,cy-104,cx+104,cy+104,fill=visual_theme.COLORS['parchment_light'],outline=BRASS,width=5)
  cv.create_oval(cx-94,cy-94,cx+94,cy+94,outline=WOOD,width=2)
  labels=[]
  for i,name in enumerate(kinds):
   angle=(i*2*math.pi/len(kinds))-math.pi/2
   x,y=cx+80*math.cos(angle),cy+80*math.sin(angle)
   cv.create_line(cx+45*math.cos(angle),cy+45*math.sin(angle),cx+98*math.cos(angle),cy+98*math.sin(angle),fill=BRASS,width=2)
   labels.append(cv.create_text(x,y,text=name,fill=INK,font=('Georgia',10,'bold')))
  def turn(step=0):
   if not win.winfo_exists():return
   selected=(spin['slot']+step+1)%len(kinds) if step<19 else spin['slot']
   for j,label in enumerate(labels):
    cv.itemconfigure(label,fill='#a65b30' if j==selected else INK,font=('Georgia',10,'bold' if j==selected else 'normal'))
   if step<19:win.after(55+step*5,lambda:turn(step+1))
  turn()
  cv.create_oval(cx-26,cy-26,cx+26,cy+26,fill=BRASS,outline=WOOD,width=3)
  cv.create_text(cx,cy,text='+'+str(spin['level']),font=('Georgia',18,'bold'),fill=INK)
  cv.create_polygon(cx-7,cy-109,cx+7,cy-109,cx,cy-96,fill='#a65b30',outline=WOOD,width=2)
  self.label(inner,spin['item']+' · '+spin['outcome']+' enchantment',14,wraplength=370).pack(pady=5)
  self.button(inner,'CONTINUE',win.destroy,True).pack(pady=8)
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
  if not self.c:return
  if self.busy:
   # Keep the newest request; never block the player or spawn many AI jobs.
   self.pending_narration=(self.c['id'],resolved)
   return
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
     pending=self.pending_narration
     self.pending_narration=None
     if pending and self.c and pending[0]==self.c['id']:
      self._narrate(pending[1])
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