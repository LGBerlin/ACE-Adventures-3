"""Background, allowlisted content updates from ACE's public release channel.

No code modules or app-bundle files can ever be installed by this updater.
Failed checks leave the last active version unchanged. Save files are separate.
"""
import json, ssl, urllib.request
from pathlib import Path
from urllib.parse import urlsplit
import update_addons

ORIGIN='https://raw.githubusercontent.com/LGBerlin/Ace-updating-versions-/main/ace-adventures-3'
MANIFEST=ORIGIN+'/latest.json'
MAX_MANIFEST=200_000
MAX_PAYLOAD=20_000_000

def _context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()

def _download(url,limit,opener=None,timeout=12):
    parsed=urlsplit(url)
    trusted=urlsplit(ORIGIN)
    if parsed.scheme!='https' or parsed.netloc!=trusted.netloc or not parsed.path.startswith(trusted.path+'/'):
        raise ValueError('Untrusted update URL')
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Update URL contains forbidden components')
    if opener is not None:
        data=opener(url)
        if not isinstance(data,bytes) or len(data)>limit:raise ValueError('Invalid update payload')
        return data
    req=urllib.request.Request(url,headers={'User-Agent':'ACE-Adventures-3/1.0'})
    with urllib.request.urlopen(req,timeout=timeout,context=_context()) as r:
        data=r.read(limit+1)
    if len(data)>limit:raise ValueError('Update payload too large')
    return data

def current(root):
    try:
        state=json.loads((Path(root)/'addons'/'active.json').read_text())
        return state.get('version') if isinstance(state,dict) else None
    except (ValueError,OSError):return None

def check_and_install(root,opener=None):
    """Returns ('updated'|'current'|'unavailable', message). Never changes saves."""
    try:
        raw=_download(MANIFEST,MAX_MANIFEST,opener)
        manifest=json.loads(raw)
        if not isinstance(manifest,dict):raise ValueError('Invalid manifest')
        version=manifest.get('version')
        if not isinstance(version,str):raise ValueError('Invalid manifest version')
        if current(root)==version:return ('current',version)
        # Abort if a newer version is already active: no involuntary downgrade.
        old=current(root)
        def parts(s):
            return tuple(int(p) for p in s.split('-')[0].split('.'))
        if old and parts(version)<=parts(old):return ('current',old)
        files=manifest.get('files')
        if not isinstance(files,list):raise ValueError('Invalid manifest entries')
        update_addons.apply(root,manifest,lambda url:_download(url,MAX_PAYLOAD,opener),ORIGIN)
        return ('updated',version)
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        return ('unavailable',type(exc).__name__)