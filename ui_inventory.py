"""Scrollable equipment and inventory folio with real, guarded item actions."""
import tkinter as tk
from tkinter import messagebox
import game
PARCH='#f0dab0';INK='#36241b';WOOD='#483022';GOLD='#aa7b3d'
CONSUMABLES=('Healing Draught','Health Potion')
def open_inventory(master,c,on_change):
    hero=c['characters'][c['active']]
    win=tk.Toplevel(master)
    win.title(hero['name']+' — Inventory & Equipment')
    win.geometry('760x700')
    win.minsize(550,510)
    win.configure(bg=WOOD)
    border=tk.Frame(win,bg=WOOD,padx=14,pady=14)
    border.pack(fill='both',expand=True)
    page=tk.Frame(border,bg=PARCH,highlightbackground=GOLD,highlightthickness=4)
    page.pack(fill='both',expand=True)
    def label(parent,text,size=12,bold=False,bg=PARCH):
        return tk.Label(parent,text=text,bg=bg,fg=INK,font=('Georgia',size,'bold' if bold else 'normal'),wraplength=320,justify='left')
    label(page,'THE ADVENTURER’S PACK',21,True).pack(pady=(20,7))
    label(page,hero['name']+'    ·    '+str(hero['gold'])+' GOLD',14).pack(pady=4)
    tk.Frame(page,bg=GOLD,height=2).pack(fill='x',padx=24,pady=10)
    equip=hero.get('equipment',{})
    label(page,'EQUIPPED',15,True).pack(anchor='w',padx=22)
    label(page,'Weapon: '+str(equip.get('weapon') or 'Empty')+'      Armor: '+str(equip.get('armor') or 'Empty'),12).pack(anchor='w',padx=24,pady=7)
    canvas=tk.Canvas(page,bg=PARCH,highlightthickness=0)
    bar=tk.Scrollbar(page,command=canvas.yview)
    frame=tk.Frame(canvas,bg=PARCH)
    frame.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
    window_id=canvas.create_window((0,0),window=frame,anchor='nw')
    canvas.bind('<Configure>',lambda e:canvas.itemconfigure(window_id,width=e.width))
    canvas.configure(yscrollcommand=bar.set)
    bar.pack(side='right',fill='y',padx=(0,12))
    canvas.pack(fill='both',expand=True,padx=16,pady=(6,18))
    if not hero['inventory']:
        label(frame,'Your pack is empty. Visit the market for supplies.').pack(pady=20)
    def action(item,use):
        try:
            if use:game.use_item(c,item)
            else:game.equip(c,item)
            on_change()
            win.destroy()
        except ValueError as err:messagebox.showwarning('Inventory',str(err),parent=win)
    for index,item in enumerate(hero['inventory']):
        outer=tk.Frame(frame,bg=WOOD,padx=3,pady=3)
        outer.grid(row=index//2,column=index%2,sticky='nsew',padx=7,pady=6)
        inner=tk.Frame(outer,bg='#fae9c8',width=280,height=106)
        inner.pack(fill='both',expand=True)
        inner.pack_propagate(False)
        label(inner,'◆  '+str(item),13,True,bg='#fae9c8').pack(anchor='w',padx=12,pady=(11,4))
        slot=game.EQUIPMENT_SLOTS.get(item)
        active=slot is not None and equip.get(slot)==item
        status='Equipped' if active else 'In your pack'
        label(inner,status,10,bg='#fae9c8').pack(anchor='w',padx=12)
        if item in CONSUMABLES or slot and not active:
            is_use=item in CONSUMABLES
            control=tk.Label(inner,text='USE' if is_use else 'EQUIP',bg=WOOD,fg='#fff0c8',
                             font=('Georgia',10,'bold'),padx=10,pady=4,cursor='hand2')
            control.pack(anchor='e',padx=12,pady=4)
            control.bind('<ButtonRelease-1>',lambda e,it=item,use=is_use:action(it,use))
    frame.grid_columnconfigure(0,weight=1)
    frame.grid_columnconfigure(1,weight=1)
    return win
