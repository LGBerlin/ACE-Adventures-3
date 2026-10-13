"""Install the 65 reviewed overall-game UI sprites into local ACE asset storage."""
from pathlib import Path
from io import BytesIO
import hashlib,json,re,sys,zipfile
from PIL import Image
DEST=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'/'overall ui'
def install(archive,destination=DEST):
 destination=Path(destination)
 with zipfile.ZipFile(archive) as z:
  prefix='ACE Adventures 3 Overall UI Pack/'
  entries=json.loads(z.read(prefix+'manifest.json'))['assets']
  if len(entries)!=65:raise ValueError('Expected 65 graphics')
  validated=[]
  for entry in entries:
   name=entry['file']
   if not isinstance(name,str) or not re.fullmatch(r'[a-z0-9_]+[.]png',name):raise ValueError('Unsafe filename')
   raw=z.read(prefix+name)
   if len(raw)>2000000 or hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('Checksum mismatch')
   with Image.open(BytesIO(raw)) as image:
    if image.format!='PNG' or max(image.size)>1200:raise ValueError('Not a valid PNG')
    if image.convert('RGBA').getchannel('A').getextrema()[0]==255:raise ValueError('Not transparent')
    image.verify()
   validated.append((name,raw))
  destination.mkdir(parents=True,exist_ok=True)
  for name,raw in validated:(destination/name).write_bytes(raw)
 return len(validated)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python install_overall_ui.py PACK.zip')
 print('Installed',install(sys.argv[1]),'overall UI sprites')
