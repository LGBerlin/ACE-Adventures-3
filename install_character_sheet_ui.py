"""Install a reviewed character-sheet UI sprite pack."""
from pathlib import Path
from io import BytesIO
import json,zipfile,hashlib,re,sys
from PIL import Image
DEST=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'/'character sheet ui'
def install(archive,destination=DEST):
 destination=Path(destination)
 with zipfile.ZipFile(archive) as z:
  prefix='ACE Adventures 3 Character Sheet UI Pack/'
  assets=json.loads(z.read(prefix+'manifest.json'))['assets']
  if len(assets)>120:raise ValueError('Too many sprites')
  validated=[]
  for item in assets:
   name=item['file']
   if not re.fullmatch(r'[a-z0-9_]+\.png',name):raise ValueError('Invalid name')
   raw=z.read(prefix+name)
   if len(raw)>2000000 or hashlib.sha256(raw).hexdigest()!=item['sha256']:raise ValueError('Invalid file')
   with Image.open(BytesIO(raw)) as img:
    if img.format!='PNG' or img.width>1200 or img.height>1200 or img.convert('RGBA').getchannel('A').getextrema()[0]==255:raise ValueError('Invalid PNG')
   validated.append((name,raw))
  destination.mkdir(parents=True,exist_ok=True)
  for name,raw in validated:(destination/name).write_bytes(raw)
 return len(validated)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python install_character_sheet_ui.py PACK.zip')
 print('Installed',install(sys.argv[1]),'UI sprites')
