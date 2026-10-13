"""Install user-provided transparent magic effects into ACE Adventures 3.

Run: python install_magic_effects.py "/path/to/ACE Adventures 3 Magic Effects Pack.zip"
"""
from pathlib import Path
import io,json,re,sys,zipfile,shutil,tempfile
from PIL import Image
from magic_effect_pack import NAME

DEST=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'/'magic effects'
def install(archive,destination=DEST):
    destination=Path(destination)
    with zipfile.ZipFile(archive) as z:
        names=z.namelist()
        files=[n for n in names if re.fullmatch(r'magic effects/effect_[0-9]{3}\.png',n)]
        if not files or len(files)>300 or len(set(files))!=len(files):
            raise ValueError('Invalid effect pack')
        mapping=json.loads(z.read('magic effects/effects.json'))
        if not isinstance(mapping,dict) or any(not NAME.fullmatch(k) or 'magic effects/'+v not in files for k,v in mapping.items()):
            raise ValueError('Invalid effect mappings')
        destination.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=destination.parent) as tmp:
            staged=Path(tmp)/'magic effects';staged.mkdir()
            for file in files:
                raw=z.read(file)
                if len(raw)>3_000_000:raise ValueError('Effect too large')
                with Image.open(io.BytesIO(raw)) as img:
                    if img.format!='PNG' or img.width>2048 or img.height>2048 or 'A' not in img.convert('RGBA').getbands():
                        raise ValueError('Invalid PNG')
                    if img.convert('RGBA').getextrema()[3][0]==255:
                        raise ValueError('Effect lacks transparency')
                    img.verify()
                (staged/Path(file).name).write_bytes(raw)
            (staged/'effects.json').write_text(json.dumps(mapping,indent=2),encoding='utf8')
            backup=destination.with_name('magic effects previous')
            if backup.exists():shutil.rmtree(backup)
            if destination.exists():destination.rename(backup)
            try:shutil.copytree(staged,destination)
            except BaseException:
                if destination.exists():shutil.rmtree(destination)
                if backup.exists():backup.rename(destination)
                raise
    return len(files)

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: python install_magic_effects.py PACK.zip')
    print('Installed',install(sys.argv[1]),'magic effects into',DEST)
