"""Install all user-reviewed artwork packs together.

Usage:
    python install_all_asset_packs.py "ACE Adventures 3 Complete Reviewed Asset Bundle.zip"

The bundle contains the individually prepared asset ZIPs. No AI-assigned art,
no gameplay rule mutation, and no network access are required.
"""
from io import BytesIO
from pathlib import Path
import zipfile,json,hashlib,sys,tempfile,shutil

ASSET_ROOT=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'
PAIRS={
 'ACE Adventures 3 Fighter Art Pack.zip':('fighter art','ACE Adventures 3 Fighter Art Pack/'),
 'ACE Adventures 3 Rogue Art Pack.zip':('rogue art','ACE Adventures 3 Rogue Art Pack/'),
 'ACE Adventures 3 Vessel Art Pack.zip':('vessel art','ACE Adventures 3 Vessel Art Pack/'),
 'ACE Adventures 3 Mage Art Pack.zip':('mage art','ACE Adventures 3 Mage Art Pack/'),
 'ACE Adventures 3 NPC Art Pack.zip':('npc art','ACE Adventures 3 NPC Art Pack/'),
 'ACE Adventures 3 Utility UI Pack.zip':('utility ui','ACE Adventures 3 Utility UI Pack/'),
 'ACE Adventures 3 Battle UI Pack.zip':('battle ui','ACE Adventures 3 Battle UI Pack/'),
 'ACE Adventures 3 Character Sheet UI Pack.zip':('character sheet ui','ACE Adventures 3 Character Sheet UI Pack/'),
 'ACE Adventures 3 Overall UI Pack.zip':('overall ui','ACE Adventures 3 Overall UI Pack/'),
 'ACE Adventures 3 Magic Effects Pack.zip':('magic effects','magic effects/'),
 'ACE Adventures 3 Battle Effects Pack.zip':('battle effects','battle effects/'),
 'ACE Adventures 3 Clean Weapons and Items Pack.zip':('items','ACE Adventures 3 Clean Weapons and Items Pack/'),
 'ACE Adventures 3 Clean Enemy Assets Pack.zip':('enemies','ACE Adventures 3 Clean Enemy Assets Pack/'),
 'ACE Adventures 3 Clean UI Sprites Pack.zip':('ui sprites','ACE Adventures 3 Clean UI Sprites Pack/'),
}
def install(bundle,root=ASSET_ROOT):
 root=Path(root)
 with zipfile.ZipFile(bundle) as outer:
  index=json.loads(outer.read('bundle manifest.json'))
  packages=index['packages']
  if set(packages)!=set(PAIRS):raise ValueError('Incomplete bundle')
  root.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=root) as tmp:
   stage=Path(tmp)/'reviewed';stage.mkdir()
   count=0
   for archive,(folder,prefix) in PAIRS.items():
    data=outer.read('packs/'+archive)
    if hashlib.sha256(data).hexdigest()!=packages[archive]['sha256']:raise ValueError('Archive checksum mismatch')
    target=stage/folder;target.mkdir()
    with zipfile.ZipFile(BytesIO(data)) as inner:
     for entry in inner.infolist():
      if entry.is_dir() or not entry.filename.startswith(prefix):continue
      rel=entry.filename[len(prefix):]
      parts=Path(rel).parts
      if not parts or any(p in ('..','.') for p in parts):raise ValueError('Unsafe path')
      if not (rel.endswith('.png') or rel.endswith('.json')):continue
      if entry.file_size>3000000:raise ValueError('Oversize sprite')
      path=target.joinpath(*parts)
      path.parent.mkdir(parents=True,exist_ok=True)
      path.write_bytes(inner.read(entry))
      if path.suffix=='.png':count+=1
   # After all validation, install packs; leave each previous version recoverable.
   for _,(folder,_) in PAIRS.items():
    dest=root/folder
    previous=root/(folder+' previous')
    if previous.exists():shutil.rmtree(previous)
    if dest.exists():dest.rename(previous)
    shutil.copytree(stage/folder,dest)
   return count
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python install_all_asset_packs.py COMPLETE.zip')
 print('Installed',install(sys.argv[1]),'reviewed PNG variants. Restart ACE Adventures 3.')
