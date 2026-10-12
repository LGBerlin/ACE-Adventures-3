"""Assemble license-tracked native game sprites from the pinned original asset archive.

The resulting images are static and intentionally compact for battery-friendly play.
"""
import csv,hashlib,io,json,random,sys,zipfile
from pathlib import Path
from PIL import Image,ImageDraw
DIGEST='df1ad1537edaedaef31d1986c3c5df54cc3c738d6db5e755e598ea9cb81421ad'
ROOT=Path(__file__).resolve().parents[1]/'assets'/'starter'
def build(archive):
 blob=Path(archive).read_bytes()
 if hashlib.sha256(blob).hexdigest()!=DIGEST:raise ValueError('Unexpected source archive')
 ROOT.mkdir(parents=True,exist_ok=True);records={};credits=[]
 def save(im,file,key,category,tags,license,author,source):
  path=ROOT/file;path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
  records[key]={'file':file,'category':category,'tags':tags,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'license':license,'author':author,'source_url':source,'review':'starter-only'}
 with zipfile.ZipFile(io.BytesIO(blob)) as outer:
  with zipfile.ZipFile(io.BytesIO(outer.read('sprites/Universal-LPC-Spritesheet-Character-Generator-master.zip'))) as z:
   base='Universal-LPC-Spritesheet-Character-Generator-master/'
   rows={r['filename']:r for r in csv.DictReader(io.StringIO(z.read(base+'CREDITS.csv').decode()))}
   used=set()
   def layer(name,color=None):
    row=rows[name];licenses=row['licenses']
    if 'OGA-BY 3.0' not in licenses and 'CC0' not in licenses:raise ValueError('Unsupported licence: '+name)
    used.add(name)
    im=Image.open(io.BytesIO(z.read(base+'spritesheets/'+name))).convert('RGBA').crop((0,128,64,192))
    if color:
     pix=im.load()
     for y in range(64):
      for x in range(64):
       r,g,b,a=pix[x,y]
       if a:
        shade=(r+g+b)/3/255
        pix[x,y]=tuple(round(c*(.35+.65*shade)) for c in color)+(a,)
    return im
   for cls,torso,color in [('Fighter','torso/armour/plate/male/walk.png',(180,190,202)),('Rogue','torso/armour/leather/male/walk.png',(68,101,73)),('Mage','torso/clothes/longsleeve/longsleeves/male/walk.png',(103,84,172)),('Vessel','torso/clothes/longsleeve/longsleeves2/male/walk.png',(177,133,65))]:
    for variant,hair in enumerate(('hair/cowlick/adult/walk.png','hair/bob/adult/walk.png','hair/buzzcut/adult/walk.png')):
     im=Image.new('RGBA',(64,64))
     for name,tint in [('body/bodies/male/walk.png',None),('head/heads/human/male/walk.png',None),('legs/pants/male/walk.png',(65,62,61)),('feet/boots/basic/male/walk.png',(80,54,36)),('torso/clothes/sleeveless/sleeveless2/male/walk.png',color),(torso,color),(hair,(79+variant*30,49+variant*25,31+variant*20))]:im.alpha_composite(layer(name,tint))
     draw=ImageDraw.Draw(im)
     if cls in ('Mage','Vessel'):
      draw.line((46,25,46,57),fill='#684830',width=2);draw.ellipse((43,19,49,27),fill='#80cfdf' if cls=='Mage' else '#acc57b',outline='#e6cf8c')
     elif cls=='Fighter':draw.line((47,23,47,54),fill='#d6dce2',width=2);draw.line((43,44,51,44),fill='#d8b46b',width=2)
     else:draw.line((45,43,49,51),fill='#d6dce2',width=2)
     im=im.crop(im.getbbox());canvas=Image.new('RGBA',(64,64));canvas.alpha_composite(im,((64-im.width)//2,64-im.height-3))
     save(canvas,f'characters/{cls.lower()}_{variant}.png',f'{cls.lower()}_{variant}','body',[f'class:{cls.lower()}'],'OGA-BY 3.0 (layers), CC0 (selected hair)','See CREDITS.csv','https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator')
   ghost=Image.open(ROOT/'characters/fighter_0.png').convert('RGBA')
   for y in range(ghost.height):
    for x in range(ghost.width):
     r,g,b,a=ghost.getpixel((x,y))
     if a:ghost.putpixel((x,y),(round(r*.55),round(g*.75),min(255,round(b*.8+35)),a))
   save(ghost,'enemies/guardian.png','guardian','body',['enemy:hollow_guardian'],'OGA-BY 3.0 (layers), CC0 (selected hair)','See CREDITS.csv','https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator')
   credits=[rows[n] for n in sorted(used)]
   (ROOT/'LPC LICENSE.txt').write_bytes(z.read(base+'LICENSE'))
  with zipfile.ZipFile(io.BytesIO(outer.read('sprites/kenney_tiny-town.zip'))) as z:
   (ROOT/'Kenney License.txt').write_bytes(z.read('License.txt'))
   def tile(i):return Image.open(io.BytesIO(z.read(f'Tiles/tile_{i:04d}.png'))).convert('RGBA').resize((32,32),Image.Resampling.NEAREST)
   tiles={i:tile(i) for i in range(132)}
   for place in ('square','market','well','forest','battle','tavern'):
    rng=random.Random(12);im=Image.new('RGBA',(800,320),'#263725')
    def put(i,x,y):im.alpha_composite(tiles[i],(x*32,y*32))
    for y in range(10):
     for x in range(25):put(25 if 11<=x<=13 else rng.choices([0,1,2],[75,24,1])[0],x,y)
    def tree(x,y):
     for dx,dy,i in [(0,0,6),(1,0,7),(2,0,8),(0,1,18),(1,1,19),(2,1,20),(0,2,30),(1,2,31),(2,2,32)]:put(i,x+dx,y+dy)
    def house(x,y):
     for dx,dy,i in [(0,0,52),(1,0,53),(2,0,54),(0,1,64),(1,1,65),(2,1,66),(0,2,72),(1,2,74),(2,2,75)]:put(i,x+dx,y+dy)
    if place in ('square','market'):
     for x,y in [(3,2),(18,2),(3,6),(18,6)]:house(x,y)
     for x,y in [(0,1),(7,0),(21,0),(7,6),(21,6)]:tree(x,y)
     if place=='market':
      for x in (8,15):
       put(81,x,5);put(83,x,4);put(107,x,6);put(104,x+1,6)
    elif place=='well':
     for x,y in [(1,1),(19,1),(3,6),(18,6)]:tree(x,y)
     put(131,12,5);put(107,15,6);put(83,10,4)
    elif place in ('forest','battle'):
     for x in (0,4,8,16,20,23):
      for y in (0,4,7):tree(x,y)
     for dx,dy,i in [(0,0,110),(1,0,111),(2,0,112),(0,1,108),(2,1,108),(0,2,108),(2,2,108)]:put(i,11+dx,1+dy)
    else:
     d=ImageDraw.Draw(im);d.rectangle((0,0,799,319),fill='#714b31')
     for y in range(0,320,24):d.line((0,y,800,y),fill='#49311f',width=2)
     for x in range(0,800,96):d.line((x,0,x,320),fill='#865d3f')
     for x in (4,10,17):
      for dx in range(3):put(81,x+dx,5)
      put(107,x,6);put(104,x+2,6)
     for x in range(2,23):put(81,x,2)
     for x in (3,8,13,18,22):put(94,x,1)
    save(im,f'backgrounds/{place}.png',place,'background',[f'location:{place}'],'CC0','Kenney','https://kenney.nl/assets/tiny-town')
 with (ROOT/'CREDITS.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=['filename','notes','authors','licenses','urls']);writer.writeheader();writer.writerows(credits)
 (ROOT/'READ ME.txt').write_text('Static starter art from the source archive; attribution in CREDITS.csv. Starter only, not final visual approval.')
 (ROOT/'manifest.json').write_text(json.dumps({'version':1,'source_archive_sha256':DIGEST,'assets':records},indent=2))
if __name__=='__main__':build(sys.argv[1])
