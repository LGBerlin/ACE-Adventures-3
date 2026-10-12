"""Lightweight, deterministic tabletop story-tree view over saved campaign facts."""
STEPS=(
 ("arrival","Arrived in Briarhollow"),
 ("elder","Accepted the Hollow Bell mystery"),
 ("mira","Learned the bell's origin from Mira"),
 ("well","Traced the carvings to Ashwood"),
 ("guardian","Confronted the Hollow Guardian"),
 ("return","Reported back to Elder Sera")
)
def timeline(c):
    q=c.get('quest') or {}
    stage=max(0,min(4,int(q.get('stage',0))))
    complete=bool(q.get('completed'))
    result=[]
    for index,(key,title) in enumerate(STEPS):
        done=(index==0 or index<=stage) if index<5 else complete
        result.append({'id':key,'title':title,'status':'completed' if done else 'current' if index==min(5,stage+1) and not complete else 'locked'})
    return result
def journal_text(c):
    return '\n'.join(('✓ ' if x['status']=='completed' else '◉ ' if x['status']=='current' else '· ')+x['title'] for x in timeline(c))
