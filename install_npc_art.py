"""Install vetted NPC PNG sprites for ACE Adventures 3."""
from pathlib import Path
from io import BytesIO
import hashlib,json,re,sys,zipfile
from PIL import Image
DEST=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'/'npc art'
def install(archive,destination=DEST):
 destination=Path(destination)
 with zipfile.ZipFile(archive) as z:
  prefix='ACE Adventures 3 NPC Art Pack/'
  entries=json.loads(z.read(prefix+'manifest.json'))['assets']
  if len(entries)>120:raise ValueError('Too many assets')
  assets=[]
  for entry in entries:
   name=entry['file']
   if not isinstance(name,str) or not re.fullmatch(r'[a-z0-9_]+[.]png',name):raise ValueError('Bad name')
   data=z.read(prefix+name)
   if hashlib.sha256(data).hexdigest()!=entry['sha256'] or len(data)>2000000:raise ValueError('Bad checksum')
   with Image.open(BytesIO(data)) as im:
    if im.format!='PNG' or im.width>1024 or im.height>1024 or im.convert('RGBA').getchannel('A').getextrema()[0]==255:raise ValueError('Bad PNG')
   assets.append((name,data))
  destination.mkdir(parents=True,exist_ok=True)
  for name,data in assets:(destination/name).write_bytes(data)
 return len(assets)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python install_npc_art.py PACK.zip')
 print('Installed',install(sys.argv[1]),'NPC sprites')
