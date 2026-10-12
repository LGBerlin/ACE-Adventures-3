"""Native canvas artwork; no external image models, fonts, or asset downloads."""
import random
from pathlib import Path
INK='#39291f';GOLD='#b18a4d';PARCH='#e9d4a8';DARK='#292b29'
def panel(cv,x,y,w,h,title='',fill=PARCH):
 cv.create_rectangle(x+5,y+6,x+w+5,y+h+6,fill='#151918',outline='')
 cv.create_rectangle(x,y,x+w,y+h,fill=fill,outline='#4b3326',width=5)
 cv.create_rectangle(x+7,y+7,x+w-7,y+h-7,outline='#aa8550',width=2)
 for xx in (x+5,x+w-5):
  for yy in (y+5,y+h-5):cv.create_oval(xx-6,yy-6,xx+6,yy+6,fill='#cda35c',outline='#775333',width=2)
 if title:
  cv.create_rectangle(x+w*.21,y-10,x+w*.79,y+21,fill='#644331',outline=GOLD,width=2)
  cv.create_text(x+w/2,y+5,text=title.upper(),fill='#f4dc9a',font=('Georgia',12,'bold'))
def character(cv,x,y,cls='Fighter',seed=7,scale=3):
 r=random.Random(seed);cloak={'Fighter':'#61717e','Rogue':'#4b7567','Mage':'#62769a','Vessel':'#98734f'}[cls]
 def block(a,b,w,h,color):cv.create_rectangle(x+a*scale,y+b*scale,x+(a+w)*scale,y+(b+h)*scale,fill=color,outline='')
 block(7,25,5,6,'#39352f');block(15,25,5,6,'#38342c');block(3,12,22,15,cloak);block(6,2,17,14,'#b78a69');block(5,1,19,4,'#403a31');block(8,10,3,2,'#302a22');block(17,10,3,2,'#302a22');block(1,16,4,11,cloak);block(24,16,4,11,cloak);block(12,15,4,9,'#ab855a')
 if cls=='Fighter':block(28,8,2,23,'#c0bfc3');block(27,6,4,7,'#d9d3bb')
 if cls=='Mage':block(28,4,3,27,'#614a36');block(26,3,7,8,'#7ec0bd')
 if cls=='Rogue':block(27,20,2,12,'#d0c5a5')
 if cls=='Vessel':block(28,4,3,29,'#8b6d46');block(26,3,7,6,'#abc084')
def _addon_background(cv,place,battle,width,height):
 """Display an optional, verified PNG background; draw native art otherwise.

 Generated imagery is treated as data, never executable code. It can be
 replaced by an asset-only update without changing gameplay or save files.
 """
 try:
  import tkinter as tk
  from update_addons import active_asset
  storage=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'
  slot='battle' if battle else place
  generated=storage/'generated'/'locations'
  custom=generated/(slot+'.png')
  path=None
  if generated.is_dir() and not generated.is_symlink() and custom.is_file() and not custom.is_symlink():
   resolved=custom.resolve()
   if resolved.is_relative_to(generated.resolve()):path=resolved
  if path is None:path=active_asset(storage,'assets/locations/'+slot+'.png')
  if path is None:return False
  image=tk.PhotoImage(master=cv,file=str(path))
  # Prefer a predictable native image size: assets are designed for 760x310.
  # Preserve the Tk image reference until canvas redraw/destruction.
  cv._ace_scene_image=image
  cv.create_image(width//2,height//2,image=image,anchor='center')
  cv.create_rectangle(5,5,width-5,height-5,outline='#c2a070',width=4)
  return True
 except (Exception):
  return False

def world(cv,place='square',battle=False,width=760,height=310):
 if _addon_background(cv,place,battle,width,height):return
 r=random.Random(61 if place=='square' else {'tavern':11,'market':21,'well':27,'forest':42}.get(place,61));w=width;h=height
 cv.configure(bg='#253a35');cv.create_rectangle(0,0,w,h,fill='#779287' if place!='tavern' else '#5f4937',outline='')
 cv.create_oval(w-160,18,w-92,86,fill='#e9d5a1',outline='')
 cv.create_polygon(0,160,w*.3,105,w*.65,176,w,103,w,h,0,h,fill='#526e5e',outline='')
 cv.create_polygon(0,210,w*.3,174,w*.66,226,w,171,w,h,0,h,fill='#45624c',outline='')
 if place=='tavern':
  cv.create_rectangle(0,60,w,h,fill='#79563d',outline='');
  for xx in range(0,w,125):cv.create_rectangle(xx,50,xx+10,h,fill='#513929',outline='')
  cv.create_rectangle(65,104,215,230,fill='#304849',outline='#392b26',width=12)
  cv.create_line(140,104,140,230,fill='#806348',width=9);cv.create_line(65,171,215,171,fill='#806348',width=9)
  cv.create_rectangle(260,221,w-70,h,fill='#5c4030',outline='#3a2c26',width=8)
  cv.create_oval(w*.62,135,w*.62+38,179,fill='#c59e76',outline='#594532',width=4)
 elif place in ('square','market'):
  cv.create_polygon(0,h,w*.4,150,w*.65,155,w,h,fill='#92866e',outline='')
  for x,y in [(65,90),(w-255,95)]:
   cv.create_rectangle(x,y,x+165,y+130,fill='#a68b6b',outline='#534638',width=5)
   cv.create_polygon(x-13,y+5,x+80,y-58,x+178,y+5,fill='#65463d',outline='#3c3331',width=6)
   cv.create_rectangle(x+60,y+70,x+103,y+130,fill='#584639',outline='')
  if place=='market':
   for x in (230,420):
    cv.create_rectangle(x,190,x+105,235,fill='#846343',outline='#3c3028',width=3)
    cv.create_polygon(x-10,185,x+45,136,x+116,185,fill='#ba7457',outline='#754734',width=3)
    for _ in range(9):
     px=x+r.randrange(15,97);py=r.randrange(198,220);cv.create_oval(px,py,px+10,py+7,fill=r.choice(['#8f9e55','#ac6355','#caab61']),outline='')
 elif place=='well':
  cv.create_oval(w*.33,192,w*.67,273,fill='#524f46',outline='#aba18c',width=14)
  cv.create_oval(w*.37,201,w*.63,251,fill='#263c43',outline='#80705c',width=7)
  cv.create_line(w*.35,207,w*.35,98,fill='#5a4030',width=10);cv.create_line(w*.65,207,w*.65,98,fill='#5a4030',width=10)
  cv.create_polygon(w*.31,100,w*.5,36,w*.69,100,fill='#6d4c3c',outline='#50382e',width=5)
 elif place=='forest':
  cv.create_polygon(0,h,w*.32,222,w*.55,231,w,h,fill='#8d8365',outline='')
  cv.create_rectangle(w*.64,133,w*.67,265,fill='#73776a',outline='#363d37',width=3)
  cv.create_rectangle(w*.77,133,w*.8,265,fill='#73776a',outline='#363d37',width=3)
  cv.create_rectangle(w*.64,133,w*.8,152,fill='#73776a',outline='#363d37',width=3)
 if place!='tavern':
  for i in range(15):
   x=r.randrange(0,w);y=r.randrange(120,210)
   if place in ('square','market') and 80<x<w-80:continue
   cv.create_rectangle(x-5,y,x+6,y+70,fill='#483f32',outline='')
   for rad,dy,col in [(33,-22,'#375947'),(27,-38,'#54735a'),(21,-53,'#638267')]:cv.create_oval(x-rad,y+dy-rad*.5,x+rad,y+dy+rad,fill=col,outline='#38513e',width=2)
 if battle:
  character(cv,130,135,'Fighter',scale=3)
  character(cv,w-210,135,'Vessel',scale=3)
  cv.create_text(w/2,24,text='THE HOLLOW GUARDIAN',fill='#f2dfb1',font=('Georgia',17,'bold'))
 cv.create_rectangle(6,6,w-6,h-6,outline='#c2a070',width=4)