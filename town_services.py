"""Repeatable guild jobs and conversational town residents.

Quest rewards are issued by code only, never by an AI narration.
"""
PEOPLE={
 "Elder Sera":{"place":"square","role":"quest giver","line":"The bell still haunts our village."},
 "Captain Rowan":{"place":"square","role":"guild captain","line":"The guild seeks capable escorts and scouts."},
 "Oren":{"place":"market","role":"merchant","line":"Good steel, fair prices."},
 "Yarrow":{"place":"market","role":"apothecary","line":"I tend travelers and hunters."},
 "Enchanter Elira":{"place":"market","role":"enchanter","line":"Bring an item and gold to enchant it."},
 "Mira":{"place":"tavern","role":"innkeeper","line":"A warm meal is always available."},
 "Tomas":{"place":"tavern","role":"townsfolk","line":"The forest has grown quiet."},
 "Nella":{"place":"square","role":"townsfolk","line":"The old roads need repair."},
}
JOBS={
 "Supply Run":{"goal":"market","reward_gold":6,"reward_xp":8},
 "Tavern Errand":{"goal":"tavern","reward_gold":5,"reward_xp":8},
 "Village Patrol":{"goal":"square","reward_gold":7,"reward_xp":10},
}
def talk(c,name):
 if not c.get("started") or c.get("enemy"):raise ValueError("Conversation is unavailable.")
 person=next((person for person in PEOPLE if person.casefold()==str(name).casefold()),None)
 if person is None or PEOPLE[person]["place"]!=c["location"]:raise ValueError("That townsfolk member is not here.")
 msg=person+": "+PEOPLE[person]["line"]
 c["history"].append(msg);c["turn"]+=1
 return msg
def accept(c,name):
 if not c.get("started") or c.get("enemy") or c.get("location")!="square":raise ValueError("Visit the guild captain in the square.")
 if name not in JOBS:raise ValueError("Unknown guild job.")
 if c.get("guild_job"):raise ValueError("Only one guild assignment can accompany the main quest: two active quests maximum.")
 c["guild_job"]={"name":name,"start_turn":c["turn"]}
 c["history"].append("Accepted guild job: "+name)
 c["turn"]+=1
 return c["history"][-1]
def complete(c):
 job=c.get("guild_job")
 if not job:raise ValueError("No active guild job.")
 details=JOBS[job["name"]]
 if c.get("enemy") or c["location"]!=details["goal"] or c["turn"]<=job["start_turn"]+1:
  raise ValueError("Complete the guild assignment before collecting your reward.")
 import game
 h=c["characters"][c["active"]]
 h["gold"]+=details["reward_gold"]
 game.award_experience(h,details["reward_xp"])
 c["guild_job"]=None
 c["history"].append("Guild job completed: "+job["name"])
 c["turn"]+=1
 return c["history"][-1]

def active_quests(c):
 """The Hollow Bell main story plus at most one guild assignment."""
 import story
 quests=[]
 if c.get("started") and not c.get("quest",{}).get("completed",False):
  quests.append({"name":"The Hollow Bell","kind":"main","stage":c.get("quest",{}).get("stage",0)})
 if c.get("guild_job"):
  quests.append({"name":c["guild_job"]["name"],"kind":"guild"})
 return quests[:2]
