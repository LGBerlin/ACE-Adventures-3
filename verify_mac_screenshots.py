"""Validate OS-captured gameplay screenshots before visual-review upload."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat

NAMES=('01 Exploration.png','02 Inventory.png','03 Shop.png','04 Battle.png','05 Story Tree.png','06 Map.png','07 Character Sheet.png','08 Abilities and Magic.png','09 Quest Journal.png','10 Dice Board.png','11 Town Services.png','12 Campaign Setup.png')

def verify(folder):
    folder=Path(folder)
    fingerprints=set()
    metrics={}
    for name in NAMES:
        file=folder/name
        if not file.is_file() or file.stat().st_size<5000:
            raise ValueError('Missing or empty real screenshot: '+name)
        with Image.open(file) as original:
            original.load()
            if original.width<900 or original.height<650:
                raise ValueError('Screenshot resolution too small: '+name)
            frame=original.convert('RGB')
            sample=frame.resize((64,36))
            signature=sample.tobytes()
            if signature in fingerprints:raise ValueError('Identical screenshots: '+name)
            fingerprints.add(signature)
            extremes=ImageStat.Stat(sample).stddev
            if max(extremes)<10:raise ValueError('Blank or flat-color screenshot: '+name)
            metrics[name]={'size':original.size,'bytes':file.stat().st_size}
    return metrics

if __name__=='__main__':
    import json
    print(json.dumps(verify('phase 2 actual screenshots'),indent=2))
