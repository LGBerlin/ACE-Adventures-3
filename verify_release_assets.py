"""Strict validation for distributable approved sprites.

Staged/unreviewed files are never considered release assets.
"""
import hashlib,json
from pathlib import Path
from PIL import Image
from sprite_coverage import report as coverage_report

def validate(root, max_decoded_pixels=4_194_304, max_bytes_per_image=4_194_304):
    root=Path(root)
    manifest=root/'manifest.json'
    errors=[]
    if not manifest.is_file():return {'ready':False,'errors':['Approved asset manifest absent']}
    try:data=json.loads(manifest.read_text(encoding='utf-8'))
    except (OSError,ValueError):return {'ready':False,'errors':['Manifest unreadable']}
    if not isinstance(data,dict) or not isinstance(data.get('assets'),dict):
        return {'ready':False,'errors':['Manifest malformed']}
    for key,item in data['assets'].items():
        if not isinstance(item,dict):
            errors.append(f'{key}: malformed asset entry')
            continue
        if item.get('review')!='approved':errors.append(f'{key}: no explicit art approval')
        if not item.get('source_url') or not item.get('author') or not item.get('license'):
            errors.append(f'{key}: provenance or licence missing')
        try:
            from asset_registry import safe_relative
            rel=safe_relative(item.get('file'))
            target=(root/str(rel)).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file():raise ValueError('missing or unsafe')
            if target.stat().st_size>max_bytes_per_image:raise ValueError('oversized file')
            content=target.read_bytes()
            if hashlib.sha256(content).hexdigest()!=item.get('sha256'):raise ValueError('checksum mismatch')
            with Image.open(target) as im:
                if im.width*im.height>max_decoded_pixels:raise ValueError('oversized decoded image')
                im.verify()
        except Exception as error:errors.append(f'{key}: {error}')
    coverage=coverage_report(root)
    if not coverage['ready']:errors.append('Incomplete class-path and spell coverage')
    return {'ready':not errors,'errors':errors,'assets':len(data['assets']),'coverage':coverage}
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('root',type=Path)
    a=parser.parse_args()
    result=validate(a.root)
    print(json.dumps(result,indent=2))
    if not result['ready']:raise SystemExit('Asset release validation failed')
