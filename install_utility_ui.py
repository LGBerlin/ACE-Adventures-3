"""Install ACE utility PNG art without changing gameplay state.

Usage: python install_utility_ui.py 'ACE Adventures 3 Utility UI Pack.zip'
"""
from pathlib import Path
from io import BytesIO
import json,zipfile,sys,tempfile,shutil,re,hashlib
from PIL import Image
DEST=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'/'utility ui'
def install(archive,destination=DEST):
 destination=Path(destination)
 with zipfile.ZipFile(archive) as z:
  prefix='ACE Adventures 3 Utility UI Pack/'
  manifest=json.loads(z.read(prefix+'manifest.json'))
  entries=manifest['assets']
  if len(entries)>300 or len(entries)<1:raise ValueError('Bad asset count')
  destination.parent.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=destination.parent) as tmp:
   staged=Path(tmp)/'utility ui';staged.mkdir()
   for entry in entries:
    name=entry['file']
    if not isinstance(name,str) or not re.fullmatch(r'[a-z0-9_]+\\.png',name):raise ValueError('Unsafe name')
    raw=z.read(prefix+name)
    if len(raw)>2_000_000 or hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('Checksum failure')
    with Image.open(BytesIO(raw)) as image:
     if image.format!='PNG' or image.width>1024 or image.height>1024:raise ValueError('Bad PNG')
     alpha=image.convert('RGBA').getchannel('A')
     if alpha.getextrema()[0]==255:raise ValueError('No transparency')
    (staged/name).write_bytes(raw)
   backup=destination.with_name('utility ui previous')
   if backup.exists():shutil.rmtree(backup)
   if destination.exists():destination.rename(backup)
   try:shutil.copytree(staged,destination)
   except BaseException:
    if destination.exists():shutil.rmtree(destination)
    if backup.exists():backup.rename(destination)
    raise
 return len(entries)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python install_utility_ui.py FILE.zip')
 print('Installed',install(sys.argv[1]),'utility UI assets')
