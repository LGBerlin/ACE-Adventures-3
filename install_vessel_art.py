"""Install named Vessel art from the review ZIP into ACE user data.

python install_vessel_art.py "ACE Adventures 3 Vessel Art Pack.zip"
"""
from pathlib import Path
from io import BytesIO
import hashlib,json,re,shutil,sys,tempfile,zipfile
from PIL import Image
DEST=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'/'vessel art'
def install(archive,destination=DEST):
 destination=Path(destination)
 with zipfile.ZipFile(archive) as z:
  prefix='ACE Adventures 3 Vessel Art Pack/'
  items=json.loads(z.read(prefix+'manifest.json'))['assets']
  if not 1<=len(items)<=100:raise ValueError('Invalid asset count')
  destination.parent.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=destination.parent) as tmp:
   staged=Path(tmp)/'vessel art';staged.mkdir()
   for entry in items:
    name=entry['name']
    if not isinstance(name,str) or not re.fullmatch(r'[a-z0-9_]+\.png',name):raise ValueError('Unsafe name')
    data=z.read(prefix+name)
    if len(data)>2000000 or hashlib.sha256(data).hexdigest()!=entry['sha256']:raise ValueError('Checksum mismatch')
    with Image.open(BytesIO(data)) as im:
     if im.format!='PNG' or im.width>1024 or im.height>1024 or im.convert('RGBA').getchannel('A').getextrema()[0]==255:raise ValueError('Invalid transparent image')
    (staged/name).write_bytes(data)
   backup=destination.with_name('vessel art previous')
   if backup.exists():shutil.rmtree(backup)
   if destination.exists():destination.rename(backup)
   try:shutil.copytree(staged,destination)
   except BaseException:
    if destination.exists():shutil.rmtree(destination)
    if backup.exists():backup.rename(destination)
    raise
 return len(items)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python install_vessel_art.py PACK.zip')
 print('Installed',install(sys.argv[1]),'Vessel sprites')
