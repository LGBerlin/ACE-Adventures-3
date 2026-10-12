"""ACE Adventures III — self-contained Mac launch baseline.
Full illustrated gameplay modules must be migrated before an official release.
"""
import json, queue, random, threading, urllib.request, tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

HOME=Path.home()/"Library"/"Application Support"/"ACE Adventures 3"
FILE=HOME/"campaigns.json"
BG="#26302e"; PAPER="#ead5ac"; INK="#39291c"; GOLD="#a9874e"
CLASSES={"Fighter":(24,5),"Rogue":(19,8),"Mage":(15,24),"Vessel":(21,16)}
PLACES={"Square":("Briarhollow Square","The village bell rings without a bellringer. Elder Rowan waits beside a rain-soaked noticeboard."),
"Tavern":("Lantern & Thistle","Mira the innkeeper polishes a glass. She has heard the bell every night."),
"Well":("Old Well","The rope is cut. Symbols have been carved into the stone rim."),
"Forest":("Ashwood Forest","The path vanishes beneath crooked trees. A guardian blocks the ruined arch.")}
def load():
 try:
  d=json.loads(FILE.read_text());return d if isinstance(d,list) else []
 except (FileNotFoundError,ValueError,OSError):return []
def save(data):
 HOME.mkdir(parents=True,exist_ok=True)
 tmp=FILE.with_suffix(".tmp");tmp.write_text(json.dumps(data,indent=2));tmp.replace(FILE)
def make(name,age,cls):
 hp,mp=CLASSES[cls]
 stats={k:random.randint(8,17) for k in ("STR","DEX","CON","INT","WIS","CHA")}
 return dict(name=name,age=int(age),cls=cls,race=random.choice(("Human","Elf","Dwarf","Orc","Gnome")),path=random.choice(("Warden","Scout","Shadow","Adept","Oracle")),hp=hp,maxhp=hp,mp=mp,maxmp=mp,stats=stats,items=["Travel Rations","Health Potion"],gold=20)
def health(url,timeout=2):
 try:
  with urllib.request.urlopen(url,timeout=timeout) as res:return json.load(res)
 except Exception:return None
class Game(tk.Tk):
 def __init__(self):
  super().__init__();self.title("ACE Adventures III");self.geometry("1130x760");self.minsize(900,620);self.configure(bg=BG)
  self.games=load();self.c=None;self.q=queue.Queue();self.active=0;self.status="";self.home();self.after(150,self.poll)
 def clear(self):
  for x in self.winfo_children():x.destroy()
 def text(self,p,s,size=13,bg=PAPER,fg=INK):
  return tk.Label(p,text=s,font=("Georgia",size),wraplength=670,justify="left",anchor="w",bg=bg,fg=fg)
 def button(self,p,s,cb):
  return tk.Button(p,text=s,command=cb,bg="#6d5035",fg="#fff1d3",font=("Georgia",12),padx=12,pady=7)
 def page(self,title):
  self.clear()
  head=tk.Frame(self,bg="#172522");head.pack(fill="x")
  self.text(head,"A.C.E. ADVENTURES III",21,"#172522","#e7d19c").pack(side="left",padx=20,pady=12)
  self.text(head,title,13,"#172522","#d9c292").pack(side="left",padx=18)
  self.button(head,"Chronicles",self.home).pack(side="right",padx=8)
  self.button(head,"AI Connections",self.connections).pack(side="right",padx=8)
  main=tk.Frame(self,bg=BG);main.pack(fill="both",expand=True,padx=17,pady=17);return main
 def panel(self,parent):
  p=tk.Frame(parent,bg=PAPER,bd=4,relief="ridge");return p
 def home(self):
  main=self.page("Campaign Library")
  p=self.panel(main);p.pack(fill="both",expand=True)
  self.text(p,"The Book of Unwritten Roads",27).pack(pady=25)
  self.button(p,"Begin a new chronicle",self.new).pack(pady=12)
  for i,c in enumerate(self.games):
   self.button(p,c["title"]+" — "+str(len(c["heroes"]))+" adventurers",lambda i=i:self.open(i)).pack(fill="x",padx=100,pady=4)
 def new(self):
  p=self.panel(self.page("New Campaign"));p.pack(fill="both",expand=True)
  self.text(p,"Name the adventure",20).pack(pady=15)
  name=tk.Entry(p,font=("Georgia",14));name.insert(0,"The Hollow Bell");name.pack(pady=7)
  self.text(p,"Number of adventurers",14).pack()
  players=tk.Spinbox(p,from_=1,to=8,width=5);players.pack(pady=8)
  def create():
   n=name.get().strip()
   if not n:return
   self.c=dict(title=n,players=int(players.get()),heroes=[],place="Square",stage=0,history=[],enemy=0,won=False)
   self.games.append(self.c);self.persist();self.creation()
  self.button(p,"Create Campaign",create).pack(pady=18)
 def persist(self):save(self.games)
 def open(self,i):
  self.c=self.games[i];self.active=0
  if len(self.c["heroes"])<self.c["players"]:self.creation()
  else:self.world()
 def creation(self):
  c=self.c;p=self.panel(self.page("Character Creation"));p.pack(fill="both",expand=True)
  self.text(p,f"Adventurer {len(c['heroes'])+1} of {c['players']}",23).pack(pady=20)
  name=tk.Entry(p,font=("Georgia",14));name.pack(pady=8);name.insert(0,"")
  age=tk.Spinbox(p,from_=10,to=120,width=8);age.pack(pady=8)
  chosen=tk.StringVar(value="Fighter")
  for cls in CLASSES:tk.Radiobutton(p,text=cls,variable=chosen,value=cls,bg=PAPER,font=("Georgia",14)).pack()
  def roll():
   if not name.get().strip():messagebox.showerror("Character","Choose a name.");return
   h=make(name.get().strip(),age.get(),chosen.get());c["heroes"].append(h);self.persist()
   messagebox.showinfo("The Fates Have Spoken",f"{h['name']} — {h['race']} {h['path']} {h['cls']}\nThis roll is permanent.")
   if len(c["heroes"])==c["players"]:self.world()
   else:self.creation()
  self.button(p,"Commit permanent character",roll).pack(pady=12)
 def world(self):
  c=self.c;p=self.page("Chapter I — The Hollow Bell")
  left=self.panel(p);left.pack(side="left",fill="both",expand=True,padx=(0,12))
  right=self.panel(p);right.pack(side="right",fill="y")
  place=c.get("place","Square");title,desc=PLACES[place]
  self.text(left,title,25).pack(anchor="w",padx=18,pady=16)
  self.text(left,desc,16).pack(anchor="w",padx=18,pady=12)
  if c.get("enemy",0)>0:self.text(left,f"Guardian health: {c['enemy']}",18).pack(pady=10)
  text=tk.Text(left,height=10,bg="#f2e3c2",fg=INK,wrap="word",font=("Georgia",13))
  text.pack(fill="both",expand=True,padx=16,pady=10)
  for line in c.get("history",[])[-10:]:text.insert("end",line+"\n\n")
  text.configure(state="disabled")
  entry=tk.Entry(left,font=("Georgia",14));entry.pack(fill="x",padx=18,pady=9)
  self.button(left,"Attempt your action (D20)",lambda:self.action(entry.get())).pack(anchor="e",padx=18,pady=6)
  self.text(right,"Adventurer's Record",19).pack(padx=12,pady=10)
  for i,h in enumerate(c["heroes"]):self.button(right,h["name"],lambda i=i:self.select(i)).pack(fill="x",padx=10,pady=3)
  h=c["heroes"][self.active]
  self.text(right,f"{h['race']} {h['path']} {h['cls']}\nHP {h['hp']}/{h['maxhp']} · Mana {h['mp']}",13).pack(padx=12,pady=10)
  self.button(right,"Character Sheet",self.sheet).pack(padx=12,pady=5)
  self.button(right,"Inventory",self.inventory).pack(padx=12,pady=5)
  available={"Square":["Tavern"],"Tavern":["Square","Well"],"Well":["Tavern","Forest"],"Forest":["Well"]}[place]
  for dest in available:
   if dest=="Well" and c["stage"]<2:continue
   if dest=="Forest" and c["stage"]<3:continue
   self.button(left,"Travel to "+dest,lambda dest=dest:self.travel(dest)).pack(anchor="w",padx=18,pady=3)
  if place=="Square" and c["stage"]==0:self.button(left,"Speak to Elder Rowan",lambda:self.story(1,"Elder Rowan asks you to question Mira at the tavern.")).pack(anchor="w",padx=18)
  if place=="Tavern" and c["stage"]==1:self.button(left,"Question Mira",lambda:self.story(2,"Mira points you towards the old well.")).pack(anchor="w",padx=18)
  if place=="Well" and c["stage"]==2:self.button(left,"Investigate the carved runes",lambda:self.story(3,"Tracks lead from the well into Ashwood.")).pack(anchor="w",padx=18)
  if place=="Forest" and c["stage"]==3 and c["enemy"]==0 and not c["won"]:self.button(left,"Approach the ruined arch",self.encounter).pack(anchor="w",padx=18)
  if place=="Square" and c["won"]:self.text(left,"Quest completed — the Hollow Bell falls silent.",18).pack(pady=15)
 def story(self,stage,line):
  self.c["stage"]=stage;self.c["history"].append(line);self.persist();self.world()
 def travel(self,place):
  self.c["place"]=place;self.persist();self.world()
 def encounter(self):
  self.c["enemy"]=18;self.c["history"].append("A Hollow Guardian bars the path. Combat begins.");self.persist();self.world()
 def action(self,s):
  s=s.strip()
  if not s:return
  c=self.c;h=c["heroes"][self.active];stat="CHA" if any(w in s.lower() for w in ("convince","talk","persuade")) else "DEX" if any(w in s.lower() for w in ("hide","dodge","sneak")) else "STR"
  dice=random.randint(1,20);total=dice+(h["stats"][stat]-10)//2;success=dice==20 or (dice!=1 and total>=12)
  line=f"{h['name']}: {s}\nD20 {dice} + {stat} modifier = {total}: {'success' if success else 'failure'}."
  if c["place"]=="Forest" and c["enemy"]>0:
   if success:c["enemy"]=max(0,c["enemy"]-random.randint(3,7))
   if c["enemy"]==0:c["won"]=True;c["stage"]=4;line+=" Guardian defeated. Return to town."
   else:h["hp"]=max(0,h["hp"]-random.randint(1,3))
  c["history"].append(line);self.persist();self.world()
 def select(self,i):self.active=i;self.world()
 def sheet(self):
  h=self.c["heroes"][self.active]
  messagebox.showinfo(h["name"]+" — Record","\n".join(f"{k}: {v}" for k,v in h["stats"].items()))
 def inventory(self):
  h=self.c["heroes"][self.active];messagebox.showinfo("Inventory","\n".join(h["items"])+f"\nGold: {h['gold']}")
 def connections(self):
  dialog=tk.Toplevel(self);dialog.title("Local AI Connections");dialog.geometry("540x250")
  label=tk.Label(dialog,text="Checking local Ollama and ComfyUI…",wraplength=490,font=("Georgia",13));label.pack(padx=25,pady=25)
  def worker():
   oll=health("http://127.0.0.1:11434/api/tags")
   comfy=health("http://127.0.0.1:8188/system_stats")
   names=[x.get("name","") for x in oll.get("models",[])] if isinstance(oll,dict) else []
   self.q.put((label,"Ollama: "+(", ".join(names) if names else "not responding or no models")+"\nComfyUI: "+("online" if comfy else "offline")+"\nAI storytelling requires Ollama configuration."))
  threading.Thread(target=worker,daemon=True).start()
 def poll(self):
  try:
   while True:
    widget,msg=self.q.get_nowait()
    if widget.winfo_exists():widget.config(text=msg)
  except queue.Empty:pass
  self.after(150,self.poll)
if __name__=="__main__":Game().mainloop()
