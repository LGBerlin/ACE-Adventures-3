"""Install the named Fighter artwork without altering gameplay or character data.

Usage: python install_fighter_art.py "ACE Adventures 3 Fighter Art Pack.zip"
"""
from pathlib import Path
from io import BytesIO
import json,sys,zipfile,tempfile,shutil,re,hashlib
from PIL import Image

DEST=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'/'fighter art'
def install(archive,destination=DEST):
 destination=Path(destination)
 prefix='ACE Adventures 3 Fighter Art Pack/'
 with zipfile.ZipFile(archive) as z:
  manifest=json.loads(z.read(prefix+'manifest.json'))
  entries=manifest.get('assets')
  if not isinstance(entries,list) or len(entries)!=35:raise ValueError('Invalid Fighter pack')
  destination.parent.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=destination.parent) as tmp:
   staged=Path(tmp)/'fighter art';staged.mkdir()
   for entry in entries:
    name=entry['name']
    if not re.fullmatch(r'(?:character|portrait|banner|nameplate|skill)_[a-z0-9_]+\.png',name):
     raise ValueError('Unsafe sprite name')
    raw=z.read(prefix+name)
    if len(raw)>2_000_000 or hashlib.sha256(raw).hexdigest()!=entry['sha256']:
     raise ValueError('Sprite checksum mismatch')
    with Image.open(BytesIO(raw)) as im:
     if im.format!='PNG' or im.width>1024 or im.height>1024 or im.convert('RGBA').getchannel('A').getextrema()[0]==255:
      raise ValueError('Invalid sprite')
     im.load()
    (staged/name).write_bytes(raw)
   backup=destination.with_name('fighter art previous')
   if backup.exists():shutil.rmtree(backup)
   if destination.exists():destination.rename(backup)
   try:shutil.copytree(staged,destination)
   except BaseException:
    if destination.exists():shutil.rmtree(destination)
    if backup.exists():backup.rename(destination)
    raise
 return len(entries)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python install_fighter_art.py PACK.zip')
 print('Installed',install(sys.argv[1]),'Fighter sprites.')
