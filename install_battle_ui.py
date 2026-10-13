"""Install the reviewed Battle UI graphics into the ACE user asset directory.

Usage: python install_battle_ui.py "ACE Adventures 3 Battle UI Pack.zip"
"""
from pathlib import Path
from io import BytesIO
import hashlib,json,re,sys,zipfile
from PIL import Image
DEST=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'/'battle ui'
def install(archive,destination=DEST):
 destination=Path(destination)
 with zipfile.ZipFile(archive) as z:
  prefix='ACE Adventures 3 Battle UI Pack/'
  assets=json.loads(z.read(prefix+'manifest.json'))['assets']
  if len(assets)!=53:raise ValueError('Expected 53 battle UI graphics')
  images=[]
  for entry in assets:
   name=entry['file']
   if not isinstance(name,str) or not re.fullmatch(r'[a-z0-9_]+[.]png',name):raise ValueError('Unsafe sprite name')
   raw=z.read(prefix+name)
   if len(raw)>2000000 or hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('Sprite checksum failed')
   with Image.open(BytesIO(raw)) as im:
    if im.format!='PNG' or im.width>1024 or im.height>512:raise ValueError('Invalid sprite')
    if im.convert('RGBA').getchannel('A').getextrema()[0]==255:raise ValueError('Sprite lacks transparent area')
    im.verify()
   images.append((name,raw))
  destination.mkdir(parents=True,exist_ok=True)
  for name,data in images:(destination/name).write_bytes(data)
 return len(images)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python install_battle_ui.py PACK.zip')
 print('Installed',install(sys.argv[1]),'Battle UI graphics')
