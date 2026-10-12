"""Opt-in, signed-by-hash add-on installation without modifying app or saves.
Manifest and payload require pre-approved trusted HTTPS origin; hashes and paths are verified.
This does not replace a full production release/signature system.
"""
import hashlib,json,os,tempfile,urllib.parse,urllib.request,re
from pathlib import Path
ALLOWED=('assets/','stories/','themes/')
def valid_path(path):
    if not isinstance(path,str):return False
    p=Path(path)
    return isinstance(path,str) and not p.is_absolute() and '..' not in p.parts and '\\' not in path and len(p.parts)>1 and path.startswith(ALLOWED) and all(part and part not in ('.','..') and not part.startswith('.') and ':' not in part for part in p.parts)
def apply(root,manifest,fetch,origin):
    root=Path(root);base=root/'addons';version=str(manifest['version'])
    # Reject filesystem redirection before touching any persistent files.
    for protected in (root,base,base/'versions',base/'active.json'):
        if protected.is_symlink():raise ValueError('Symbolic links in update storage are not permitted')
    if not re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}(?:-[a-zA-Z0-9]+)?',version):raise ValueError('Invalid version')
    dest=base/'versions'/version
    if dest.exists():raise ValueError('Version already installed')
    files=manifest['files'];entries=[];seen=set();total_bytes=0
    if not isinstance(files,list):raise ValueError('Invalid add-on file list')
    trusted=urllib.parse.urlsplit(origin)
    if trusted.scheme!='https' or not trusted.netloc or trusted.username or trusted.password or trusted.query or trusted.fragment:
        raise ValueError('Invalid trusted origin')
    if not files or len(files)>500:raise ValueError('Invalid file count')
    for item in files:
        if not isinstance(item,dict):raise ValueError('Invalid add-on file entry')
        path=item['path'];url=item['url'];expected=item['sha256']
        if not isinstance(url,str) or not isinstance(expected,str):raise ValueError('Invalid URL or checksum type')
        if not valid_path(path) or path in seen:raise ValueError('Invalid or duplicate add-on path')
        seen.add(path)
        parsed=urllib.parse.urlsplit(url)
        if parsed.scheme!='https' or parsed.netloc!=trusted.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment or not parsed.path.startswith(trusted.path.rstrip('/')+'/'):raise ValueError('Untrusted add-on source')
        if len(expected)!=64 or any(ch not in '0123456789abcdef' for ch in expected):raise ValueError('Invalid checksum')
        blob=fetch(url)
        if not isinstance(blob,bytes):raise ValueError('Non-binary update payload')
        if len(blob)>20_000_000 or hashlib.sha256(blob).hexdigest()!=expected:raise ValueError('Checksum mismatch')
        total_bytes+=len(blob)
        if total_bytes>80_000_000:raise ValueError('Add-on exceeds size limit')
        entries.append((path,blob))
    dest.mkdir(parents=True)
    try:
        for path,blob in entries:
            target=dest/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
        base.mkdir(parents=True,exist_ok=True)
        marker=base/'active.json';previous=None
        if marker.exists():previous=json.loads(marker.read_text()).get('version')
        with tempfile.NamedTemporaryFile('w',dir=base,delete=False) as tmp:
            json.dump({'version':version,'previous':previous},tmp);name=tmp.name
        os.replace(name,marker)
    except Exception:
        import shutil
        shutil.rmtree(dest,ignore_errors=True)
        raise
    return version
def rollback(root):
    marker=Path(root)/'addons'/'active.json';d=json.loads(marker.read_text());prev=d.get('previous')
    if prev is None:
        marker.unlink()
    else:
        if not re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}(?:-[a-zA-Z0-9]+)?',prev):
            raise ValueError('Invalid previous version')
        previous_dir=marker.parent/'versions'/prev
        if not previous_dir.is_dir() or previous_dir.is_symlink():
            raise ValueError('Previous update missing; keeping current update')
        with tempfile.NamedTemporaryFile('w',dir=marker.parent,delete=False) as tmp:
            json.dump({'version':prev,'previous':None},tmp);temp_name=tmp.name
        os.replace(temp_name,marker)

def active_asset(root,relative_path):
    """Find a verified add-on asset without permitting path traversal or symlink escapes.

    A missing or corrupt active marker simply falls back to bundled artwork.
    This function never mutates save files or changes an installed version.
    """
    if not valid_path(relative_path):
        raise ValueError('Invalid add-on asset path')
    base=Path(root)/'addons'
    marker=base/'active.json'
    try:
        data=json.loads(marker.read_text(encoding='utf-8'))
        version=data['version']
        if not isinstance(version,str) or not re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}(?:-[a-zA-Z0-9]+)?',version):return None
        directory=(base/'versions'/version).resolve(strict=True)
        allowed=(base/'versions').resolve(strict=True)
        if not directory.is_relative_to(allowed):return None
        asset=directory/relative_path
        resolved=asset.resolve(strict=True)
        if not resolved.is_relative_to(directory) or not resolved.is_file():return None
        return resolved
    except (OSError,ValueError,KeyError,TypeError,RuntimeError):
        return None