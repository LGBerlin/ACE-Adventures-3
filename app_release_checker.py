"""Manual, non-invasive macOS application release availability checks.

Never modifies, patches, deletes or swaps the running .app bundle.
Future installers must be separately verified, code-signed, and explicitly approved.
"""
import json,re,urllib.request
from urllib.parse import urlsplit
RELEASES='https://api.github.com/repos/LGBerlin/ACE-Adventures-3/releases/latest'
VERSION=re.compile(r'^v?(\d+)\.(\d+)\.(\d+)$')
def parse_version(v):
    if not isinstance(v,str):raise ValueError('Invalid release version')
    match=VERSION.fullmatch(v)
    if not match:raise ValueError('Unsupported app release version')
    return tuple(map(int,match.groups()))
def check(current,request=None):
    """Return URL and verified metadata for human approval; never execute downloads."""
    old=parse_version(current)
    try:
        if request is None:
            req=urllib.request.Request(RELEASES,headers={'User-Agent':'ACE-Adventures-3/1.0','Accept':'application/vnd.github+json'})
            with urllib.request.urlopen(req,timeout=8) as response:
                data=json.load(response)
        else:data=request()
        if not isinstance(data,dict) or data.get('draft') or data.get('prerelease'):
            return {'status':'unavailable'}
        new=parse_version(data['tag_name'])
        if new<=old:return {'status':'current'}
        assets=data.get('assets')
        if not isinstance(assets,list):raise ValueError('Invalid assets')
        choices=[a for a in assets if isinstance(a,dict) and a.get('name')=='ACE Adventures 3 Mac App.zip']
        if len(choices)!=1:raise ValueError('Signed Mac application archive not found')
        link=choices[0].get('browser_download_url')
        if not isinstance(link,str):raise ValueError('Invalid download link')
        parsed=urlsplit(link)
        if parsed.scheme!='https' or parsed.netloc!='github.com' or not parsed.path.startswith('/LGBerlin/ACE-Adventures-3/releases/download/') or parsed.query or parsed.fragment:
            raise ValueError('Untrusted app download link')
        return {'status':'available','version':data['tag_name'],'download_url':link,
                'note':'Manual install only. No in-place app replacement or code execution.'}
    except (OSError,ValueError,KeyError,TypeError):
        return {'status':'unavailable'}
