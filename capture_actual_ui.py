"""Capture genuine running Mac application UI, never concept renders.

Screenshots are optional diagnostics: macOS CI may deny screen capture.
"""
import hashlib,os,subprocess,sys,tempfile,time
from pathlib import Path
from PIL import Image
import random
import app,game,ui_character_sheet,ui_inventory,ui_shop

OUT=Path(sys.argv[1] if len(sys.argv)>1 else 'actual-ui-screenshots').resolve()
OUT.mkdir(parents=True,exist_ok=True)
original=app.DATA
sampledir=tempfile.TemporaryDirectory(prefix='ace-screen-')
app.DATA=Path(sampledir.name)
win=app.App()
win.geometry('1300x880+25+45')
win.lift()
def present():
    win.deiconify();win.update_idletasks();win.update();time.sleep(1)
def snap(filename):
    present()
    path=OUT/filename
    cmd=subprocess.run(['screencapture','-x',str(path)],capture_output=True,text=True,timeout=12)
    if cmd.returncode or not path.is_file():
        print('Mac display capture unavailable:',cmd.stderr.strip())
        return False
    try:
        with Image.open(path) as im:
            if im.width<850 or im.height<550:raise ValueError('Unexpected screen size')
            extremes=im.convert('RGB').getextrema()
            if max(pair[1]-pair[0] for pair in extremes)<20:raise ValueError('Blank screenshot')
    except (OSError,ValueError) as e:
        print('Rejecting unreliable capture:',e);path.unlink(missing_ok=True);return False
    return True
try:
    win._new()
    snap('01 Character Creation.png')
    c=game.new_campaign('Screenshot Chronicle',1)
    hero=game.character('Arlen',26,'Mage',random.Random(7))
    game.add_hero(c,hero);game.start(c)
    win.c=c;win._adventure()
    snap('02 Adventure.png')
    detail=ui_character_sheet.open_sheet(win,hero)
    detail.lift();snap('03 Character Sheet.png');detail.destroy()
    detail=ui_inventory.open_inventory(win,c,lambda:None)
    detail.lift();snap('04 Inventory.png');detail.destroy()
    c['location']='market';win._adventure()
    detail=ui_shop.open_shop(win,c,lambda:None)
    detail.lift();snap('05 Market Shop.png');detail.destroy()
    c['location']='forest';game.encounter(c,random.Random(4));win._adventure()
    snap('06 Battle.png')
finally:
    win.destroy();app.DATA=original;sampledir.cleanup()
files=sorted(OUT.glob('*.png'))
if len(files)>=2:
    digests={hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    if len(digests)<2:
        print('Capture did not reflect different UI states; removing unreliable images')
        for p in files:p.unlink()
print('Genuine usable screenshots:',len(list(OUT.glob('*.png'))))
