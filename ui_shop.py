"""Actual market shop screen; purchases are validated by shop.py, never by AI prose."""
import tkinter as tk
from tkinter import messagebox
import shop
PARCH='#f0dab0';INK='#35241c';WOOD='#483022';GOLD='#aa7b3d'
def open_shop(master,c,on_change):
    if c.get('location')!='market' or c.get('enemy'):
        raise ValueError('Visit the market outside combat to shop.')
    hero=c['characters'][c['active']]
    window=tk.Toplevel(master)
    window.title('Yarrow’s Apothecary — Market')
    window.geometry('780x700')
    window.minsize(570,510)
    window.configure(bg=WOOD)
    paper=tk.Frame(window,bg=PARCH,highlightbackground=GOLD,highlightthickness=4)
    paper.pack(fill='both',expand=True,padx=14,pady=14)
    def label(parent,value,size=12,bold=False):
        return tk.Label(parent,text=value,font=('Georgia',size,'bold' if bold else 'normal'),
                        fg=INK,bg=parent.cget('bg'),wraplength=295,justify='left')
    label(paper,'YARROW’S APOTHECARY',22,True).pack(pady=(22,6))
    label(paper,'Supplies for the roads beyond Briarhollow',12).pack(pady=3)
    label(paper,'YOUR PURSE  ◈  '+str(hero['gold'])+' GOLD',14,True).pack(pady=10)
    tk.Frame(paper,bg=GOLD,height=2).pack(fill='x',padx=22,pady=7)
    canvas=tk.Canvas(paper,bg=PARCH,highlightthickness=0)
    scrollbar=tk.Scrollbar(paper,command=canvas.yview)
    listing=tk.Frame(canvas,bg=PARCH)
    listing.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
    window_id=canvas.create_window((0,0),window=listing,anchor='nw')
    canvas.bind('<Configure>',lambda e:canvas.itemconfigure(window_id,width=e.width))
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right',fill='y',padx=(0,10))
    canvas.pack(fill='both',expand=True,padx=16,pady=(8,18))
    def purchase(name):
        try:
            shop.buy(c,name)
            on_change()
            window.destroy()
        except ValueError as error:messagebox.showwarning('Merchant',str(error),parent=window)
    for i,(name,item) in enumerate(shop.CATALOG.items()):
        border=tk.Frame(listing,bg=WOOD,padx=3,pady=3)
        border.grid(row=i//2,column=i%2,sticky='nsew',padx=7,pady=7)
        card=tk.Frame(border,bg='#fae9c8',height=137)
        card.pack(fill='both',expand=True)
        card.pack_propagate(False)
        label(card,'◈  '+name,14,True).pack(anchor='w',padx=12,pady=(12,4))
        label(card,item['description'],11).pack(anchor='w',padx=12)
        footer=tk.Frame(card,bg=card.cget('bg'))
        footer.pack(fill='x',side='bottom',padx=11,pady=10)
        label(footer,str(item['price'])+' gold',12,True).pack(side='left')
        buy=tk.Label(footer,text='BUY',bg=WOOD,fg='#fff0c8',font=('Georgia',11,'bold'),
                     padx=14,pady=5,cursor='hand2')
        buy.pack(side='right')
        buy.bind('<ButtonRelease-1>',lambda e,n=name:purchase(n))
    listing.grid_columnconfigure(0,weight=1)
    listing.grid_columnconfigure(1,weight=1)
    return window
