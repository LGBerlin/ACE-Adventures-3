"""Install a locally supplied ACE art pack after validation.

Usage: python install_art_pack.py "ACE Adventures 3 Art Pack.zip"
"""
from pathlib import Path, PurePosixPath
import hashlib, json, sys, zipfile, tempfile, shutil
from asset_registry import Registry, safe_relative

def install(archive, destination):
    archive=Path(archive)
    destination=Path(destination)
    with zipfile.ZipFile(archive) as source:
        if len(source.infolist())>1500:
            raise ValueError("Excessive number of files")
        manifest=json.loads(source.read("approved sprites/manifest.json"))
        if manifest.get("version")!=1 or not isinstance(manifest.get("assets"),dict):
            raise ValueError("Bad manifest")
        if len(manifest["assets"])>1000:
            raise ValueError("Too many sprites")
        with tempfile.TemporaryDirectory(dir=destination.parent if destination.parent.exists() else None) as directory:
            staging=Path(directory)/"approved sprites"
            staging.mkdir(parents=True)
            written=set()
            for name,item in manifest["assets"].items():
                path=safe_relative(item["file"])
                member="approved sprites/"+str(path)
                if member in written:
                    raise ValueError("Duplicate member")
                written.add(member)
                info=source.getinfo(member)
                if info.file_size>4*1024*1024 or info.file_size==0:
                    raise ValueError("Invalid sprite size")
                raw=source.read(member)
                if hashlib.sha256(raw).hexdigest()!=item["sha256"]:
                    raise ValueError("Sprite checksum mismatch: "+member)
                target=staging/path
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(raw)
            (staging/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
            reg=Registry(staging,staging/"manifest.json")
            if any(reg.bytes(key) is None for key in reg.records):
                raise ValueError("Sprite pack verification failed")
            # Do not destroy a previous pack until the new one is validated.
            destination.parent.mkdir(parents=True,exist_ok=True)
            backup=destination.with_name(destination.name+" previous")
            if backup.exists():
                shutil.rmtree(backup)
            if destination.exists():
                destination.rename(backup)
            try:
                shutil.copytree(staging,destination)
            except BaseException:
                if destination.exists():
                    shutil.rmtree(destination)
                if backup.exists():
                    backup.rename(destination)
                raise
    return len(manifest["assets"])

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python install_art_pack.py ART_PACK.zip")
    location=Path.home()/"Library"/"Application Support"/"ACE Adventures 3"/"approved sprites"
    print("Installed",install(sys.argv[1],location),"art assets to",location)
