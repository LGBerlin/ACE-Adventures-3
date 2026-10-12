"""Authoritative market trading rules. Shops never trust model-generated prices."""
CATALOG={'Healing Draught':{'price':9,'description':'Restores 12 HP'},
         'Health Potion':{'price':7,'description':'Restores 8 HP'},
         'Travel Rations':{'price':3,'description':'Food for the road'},
         'Rope':{'price':5,'description':'Fifty feet of hemp rope'},
         'Torch':{'price':2,'description':'A light for dark passages'}}
def buy(c,name):
    if not c.get('started'):raise ValueError('Start your adventure before shopping.')
    if c.get('enemy'):raise ValueError('You cannot shop during combat.')
    if c.get('location')!='market':raise ValueError('Visit the market to buy supplies.')
    if name not in CATALOG:raise ValueError('The merchant does not stock that item.')
    hero=c['characters'][c['active']]
    price=CATALOG[name]['price']
    if hero['gold']<price:raise ValueError('Not enough gold.')
    hero['gold']-=price
    hero['inventory'].append(name)
    result=f"{hero['name']} buys {name} for {price} gold."
    c['history'].append(result)
    c['turn']+=1
    return result
