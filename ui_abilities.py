"""Static illustrated-style spellbook and technique folio for every class."""
import tkinter as tk
import game,spell_catalog,technique_catalog
INK='#35251b';PARCH='#f1dfbb';WOOD='#483022';GOLD='#ac803f'
SCHOOL_COLORS={'Earth':'#7f6135','Water':'#275d8b','Air':'#657989','Fire':'#a84925',
               'Lightning':'#a27615','Gravity':'#5a497b','Blood':'#942e38','Illusion':'#79518a',
               'Light':'#b38423','Dark':'#50455b','Support':'#477b64','Time':'#466c92',
               'Creation':'#517457','Chaos':'#8d3c75'}
def entries(hero):
    if hero['class']=='Mage' and hero.get('magic') in spell_catalog.MAGIC_TYPES:
        return spell_catalog.catalog(hero['magic'])
    return [{'name':x,'level':1} for x in game.MOVES.get(hero['path'],[])]+technique_catalog.catalog(hero['path'])
def open_abilities(master,hero):
    win=tk.Toplevel(master);win.title(hero['name']+' — Spellbook & Techniques')
    win.geometry('760x705');win.minsize(550,480);win.configure(bg=WOOD)
    paper=tk.Frame(win,bg=PARCH,highlightbackground=GOLD,highlightthickness=4)
    paper.pack(fill='both',expand=True,padx=14,pady=14)
    def label(parent,value,size=12,bold=False):
        return tk.Label(parent,text=value,bg=parent.cget('bg'),fg=INK,font=('Georgia',size,'bold' if bold else 'normal'),
                        justify='left',wraplength=300)
    label(paper,'THE BOOK OF ABILITIES',22,True).pack(pady=(21,8))
    label(paper,hero['name']+'  ·  '+game.display_archetype(hero)+'  ·  Level '+str(hero['level']),14).pack()
    if hero['class']=='Mage':label(paper,'MAGIC SCHOOL  ·  '+hero['magic'],13,True).pack(pady=9)
    tk.Frame(paper,bg=GOLD,height=2).pack(fill='x',padx=24,pady=(10,6))
    container=tk.Frame(paper,bg=PARCH)
    container.pack(fill='both',expand=True,padx=15,pady=10)
    canvas=tk.Canvas(container,bg=PARCH,highlightthickness=0)
    scroller=tk.Scrollbar(container,command=canvas.yview)
    cards=tk.Frame(canvas,bg=PARCH)
    cards.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
    wid=canvas.create_window((0,0),window=cards,anchor='nw')
    canvas.bind('<Configure>',lambda e:canvas.itemconfigure(wid,width=e.width))
    canvas.configure(yscrollcommand=scroller.set)
    scroller.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True)
    for i,ability in enumerate(entries(hero)):
        known=ability['name'] in hero['moves'] and ability['level']<=hero['level']
        border=tk.Frame(cards,bg=GOLD if known else '#847969',padx=3,pady=3)
        border.grid(row=i//2,column=i%2,sticky='nsew',padx=7,pady=7)
        tile=tk.Frame(border,bg='#faebc9',height=115)
        tile.pack(fill='both',expand=True)
        tile.pack_propagate(False)
        circle=tk.Canvas(tile,width=28,height=28,highlightthickness=0,bg='#faebc9')
        circle.pack(side='left',padx=10)
        fill=SCHOOL_COLORS.get(hero.get('magic'),WOOD)
        circle.create_oval(3,3,25,25,fill=fill if known else '#b5aa93',outline=GOLD,width=2)
        info=tk.Frame(tile,bg=tile.cget('bg'))
        info.pack(fill='both',expand=True,pady=10)
        label(info,ability['name'],13,True).pack(anchor='w')
        label(info,'READY' if known else 'UNLOCKS AT LEVEL '+str(ability['level']),10,True).pack(anchor='w',pady=6)
    cards.grid_columnconfigure(0,weight=1);cards.grid_columnconfigure(1,weight=1)
    return win
