"""Capture *actual running Tk windows* on macOS for visual review.

No art generation. These PNGs are OS-level screen captures of the application.
They are review evidence, not assertions of aesthetic fidelity.
"""
import random
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import app
import game
import story

def capture(ui,location,destination):
    ui._adventure()
    if location!='Record':ui._panel(location)
    ui.deiconify()
    ui.lift()
    ui.update()
    ui.update_idletasks()
    time.sleep(0.5)
    ui.update()
    shot=destination
    proc=subprocess.run(['screencapture','-x',str(shot)],capture_output=True,text=True,timeout=12)
    if proc.returncode or not shot.is_file() or shot.stat().st_size<5000:
        raise RuntimeError('macOS screen capture failed: '+proc.stderr.strip())
    print('Captured running game:',shot,shot.stat().st_size)

def main():
    if sys.platform!='darwin':
        raise SystemExit('Screenshots must be captured by macOS itself.')
    root=Path('phase 2 actual screenshots').resolve()
    root.mkdir(exist_ok=True)
    with patch.object(app,'DATA',root/'test campaign data'):
        ui=app.App()
        try:
            ui.geometry('1300x880+50+50')
            campaign=game.new_campaign('Screenshot Review',4)
            for i,cls in enumerate(('Fighter','Rogue','Mage','Vessel')):
                game.add_hero(campaign,game.character(('Arin','Syl','Iris','Vale')[i],25,cls,random.Random(i+14)))
            game.start(campaign)
            story.ensure(campaign)
            ui.c=campaign
            capture(ui,'Record',root/'01 Exploration.png')
            ui._panel('Pack')
            capture(ui,'Pack',root/'02 Inventory.png')
            campaign['location']='market'
            capture(ui,'Shop',root/'03 Shop.png')
            campaign['location']='forest'
            campaign['enemy']={'name':'Hollow Guardian','hp':22,'max_hp':30,'ac':14,'boss':True,'phase':2}
            capture(ui,'Abilities',root/'04 Battle.png')
            campaign['enemy']=None
            campaign['location']='square'
            capture(ui,'Story Tree',root/'05 Story Tree.png')
            capture(ui,'Map',root/'06 Map.png')
        finally:
            ui.destroy()
    print('Six screenshots captured by macOS screen capture utility.')
if __name__=='__main__':
    main()
