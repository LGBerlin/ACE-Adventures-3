"""High-contrast, scrollable illustrated character-sheet window.

Pure Tk controls, static draw operations, no background refresh or AI generation.
"""
import tkinter as tk
from tkinter import ttk
import game

PARCH='#f4e3bf'
INK='#34261d'
WOOD='#493020'
GOLD='#a77b3c'

def open_sheet(master, hero):
    window=tk.Toplevel(master)
    window.title(hero['name']+' — Character Sheet')
    window.geometry('690x760')
    window.minsize(520,560)
    window.configure(bg=WOOD)
    outer=tk.Frame(window,bg=WOOD,padx=14,pady=14)
    outer.pack(fill='both',expand=True)
    paper=tk.Frame(outer,bg=PARCH,highlightbackground=GOLD,highlightthickness=4)
    paper.pack(fill='both',expand=True)
    title=tk.Label(paper,text=hero['name'].upper(),font=('Georgia',24,'bold'),fg=INK,bg=PARCH)
    title.pack(pady=(20,5))
    subtitle=f"{hero['class']}  ·  {game.display_archetype(hero)}  ·  Level {hero['level']}"
    tk.Label(paper,text=subtitle,font=('Georgia',14),fg=INK,bg=PARCH).pack(pady=3)
    tk.Frame(paper,bg=GOLD,height=2).pack(fill='x',padx=22,pady=13)
    canvas=tk.Canvas(paper,bg=PARCH,highlightthickness=0)
    scrollbar=tk.Scrollbar(paper,orient='vertical',command=canvas.yview)
    interior=tk.Frame(canvas,bg=PARCH)
    interior.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
    canvas.create_window((0,0),window=interior,anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right',fill='y',padx=(0,7))
    canvas.pack(side='left',fill='both',expand=True,padx=16,pady=(0,14))
    def heading(value):
        tk.Label(interior,text=value,font=('Georgia',15,'bold'),fg='#744322',bg=PARCH).pack(anchor='w',pady=(15,7))
    def entry(value):
        tk.Label(interior,text=value,font=('Georgia',12),fg=INK,bg=PARCH,anchor='w',justify='left',wraplength=565).pack(anchor='w',pady=3)
    heading('THE ADVENTURER')
    entry(f"Age {hero['age']}  ·  Magic {hero.get('magic','None')}")
    entry(f"Health {hero['hp']} / {hero['max_hp']}  ·  Mana {hero['mana']} / {hero['max_mana']}")
    entry(f"Experience {hero['xp']}  ·  Gold {hero['gold']}")
    heading('ABILITIES & MODIFIERS')
    for key in ('STR','DEX','CON','INT','WIS','CHA'):
        value=hero['stats'][key]
        entry(f"{key:4s}     {value:2d}       {(value-10)//2:+d}")
    heading('TRAINING & TECHNIQUES')
    for name in hero.get('skills',[]):entry('Skill  ·  '+name)
    for name in hero.get('moves',[]):entry('◆  '+name)
    for name in hero.get('passives',[]):entry('◇  '+name)
    heading('INVENTORY')
    for name in hero.get('inventory',[]):entry('◈  '+str(name))
    def wheel(event):
        canvas.yview_scroll(-1 if event.delta>0 else 1,'units')
    canvas.bind('<MouseWheel>',wheel)
    return window
