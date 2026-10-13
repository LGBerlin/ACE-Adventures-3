"""Install reviewed Rogue artwork from a ZIP.

python install_rogue_art.py 'ACE Adventures 3 Rogue Art Pack.zip'
"""
import hashlib,json,re,shutil,sys,tempfile,zipfile
from io import BytesIO
from pathlib import Path
from PIL import Image
DEST=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'/'rogue art'
def install(archive,destination=DEST):
 destination=Path(destination)
 with zipfile.ZipFile(archive) as z:
  prefix='ACE Adventures 3 Rogue Art Pack/'
  manifest=json.loads(z.read(prefix+'manifest.json'))
  entries=manifest['assets']
  if len(entries)>100 or len(entries)<1:raise ValueError('Invalid sprite count')
  destination.parent.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=destination.parent) as tmp:
   staged=Path(tmp)/'rogue art';staged.mkdir()
   for item in entries:
    name=item['name']
    if not isinstance(name,str) or not re.fullmatch(r'[a-z0-9_]+\.png',name):raise ValueError('Unsafe PNG name')
    content=z.read(prefix+name)
    if len(content)>2000000 or hashlib.sha256(content).hexdigest()!=item['sha256']:raise ValueError('Invalid image checksum')
    with Image.open(BytesIO(content)) as image:
     if image.format!='PNG' or image.width>1024 or image.height>1024 or image.convert('RGBA').getchannel('A').getextrema()[0]==255:
      raise ValueError('Not a valid transparent PNG')
    (staged/name).write_bytes(content)
   old=destination.with_name('rogue art previous')
   if old.exists():shutil.rmtree(old)
   if destination.exists():destination.rename(old)
   try:shutil.copytree(staged,destination)
   except BaseException:
    if destination.exists():shutil.rmtree(destination)
    if old.exists():old.rename(destination)
    raise
 return len(entries)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python install_rogue_art.py PACK.zip')
 print('Installed',install(sys.argv[1]),'Rogue sprite assets')
