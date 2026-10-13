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
 "Village Patrol":{"goal":"tavern","reward_gold":7,"reward_xp":10},
 "Herbalist Consultation":{"goal":"market","npc":"Yarrow","reward_gold":9,"reward_xp":12},
 "Inn Rumors":{"goal":"tavern","npc":"Tomas","reward_gold":8,"reward_xp":10},
 "Medicine Delivery":{"goal":"market","item":"Healing Draught","reward_gold":16,"reward_xp":14},
 "Armory Requisition":{"goal":"market","item":"Iron Sword","reward_gold":26,"reward_xp":20,"requires_jobs":2},
 "Veteran Reconnaissance":{"goal":"tavern","npc":"Tomas","reward_gold":22,"reward_xp":24,"requires_jobs":4},
}
def note_conversation(c,person):
 """Record a conversation whichever narrative handler owns that NPC."""
 job=c.get("guild_job")
 if not job:return False
 spec=JOBS.get(job["name"],{})
 if spec.get("npc")==person and c.get("location")==spec.get("goal") and c.get("turn",0)>job["start_turn"]:
  job["spoke_to_target"]=True
  return True
 return False

def talk(c,name):
 if not c.get("started") or c.get("enemy"):raise ValueError("Conversation is unavailable.")
 person=next((person for person in PEOPLE if person.casefold()==str(name).casefold()),None)
 if person is None or PEOPLE[person]["place"]!=c["location"]:raise ValueError("That townsfolk member is not here.")
 memory=c.setdefault("town_memory",{})
 count=memory.get(person,0)
 line=PEOPLE[person]["line"]
 if count>0:
  line+=" Welcome back." if count==1 else " You've become a familiar face."
 memory[person]=min(count+1,100)
 msg=person+": "+line
 if note_conversation(c,person):
  msg+=" You have gathered the information for your guild assignment."
 c["history"].append(msg);c["turn"]+=1
 return msg
def accept(c,name):
 if not c.get("started") or c.get("enemy") or c.get("location")!="square":raise ValueError("Visit the guild captain in the square.")
 if name not in JOBS:raise ValueError("Unknown guild job.")
 if c.get("guild_jobs_completed",0)<JOBS[name].get("requires_jobs",0):raise ValueError("Higher guild reputation is required for this assignment.")
 if c.get("guild_job"):raise ValueError("Only one guild assignment can accompany the main quest: two active quests maximum.")
 c["guild_job"]={"name":name,"start_turn":c["turn"],"origin":c["location"],"visited_goal":False,"spoke_to_target":False}
 c["history"].append("Accepted guild job: "+name)
 c["turn"]+=1
 return c["history"][-1]
def note_travel(c,place):
 """Only actual travel after accepting a job can satisfy its destination."""
 job=c.get("guild_job")
 if job and place==JOBS[job["name"]]["goal"] and c.get("turn",0)>job["start_turn"]:
  job["visited_goal"]=True

def complete(c):
 job=c.get("guild_job")
 if not job:raise ValueError("No active guild job.")
 details=JOBS[job["name"]]
 if c.get("enemy") or not job.get("visited_goal") or (details.get("npc") and not job.get("spoke_to_target")):
  raise ValueError("Visit the guild destination before collecting a reward.")
 if c.get("location")!="square":
  raise ValueError("Return to Captain Rowan in the square to claim your reward.")
 import game
 h=c["characters"][c["active"]]
 item=details.get("item")
 if item and item not in h["inventory"]:
  raise ValueError("Bring the required item to the guild captain.")
 if item:h["inventory"].remove(item)
 h["gold"]+=details["reward_gold"]
 game.award_experience(h,details["reward_xp"])
 c["guild_job"]=None
 c["guild_jobs_completed"]=c.get("guild_jobs_completed",0)+1
 c["history"].append("Guild job completed: "+job["name"])
 c["turn"]+=1
 return c["history"][-1]

def abandon(c):
 """Only the optional guild assignment may be abandoned; main story is permanent."""
 if not c.get("guild_job"):raise ValueError("No optional guild job to abandon.")
 if c.get("enemy"):raise ValueError("Cannot abandon quests during combat.")
 job=c["guild_job"]["name"]
 c["guild_job"]=None
 c["history"].append("Guild assignment abandoned: "+job)
 c["turn"]+=1
 return c["history"][-1]

def active_quests(c):
 """The Hollow Bell main story plus at most one guild assignment."""
 import story
 quests=[]
 if c.get("started") and not c.get("quest",{}).get("completed",False):
  stage=c.get("quest",{}).get("stage",0)
  stage=max(0,min(len(story.STAGES)-1,stage)) if isinstance(stage,int) else 0
  quests.append({"name":"The Hollow Bell","kind":"main","stage":stage,"objective":story.STAGES[stage]})
 if c.get("guild_job"):
  quests.append({"name":c["guild_job"]["name"],"kind":"guild"})
 return quests[:2]

def quest_status(c):
 """Read-only quest objectives, safe for narration and free-text status commands."""
 entries=active_quests(c)
 job=c.get("guild_job")
 if job:
  spec=JOBS[job["name"]]
  if not job.get("visited_goal"):
   objective="Travel to the "+spec["goal"]
  elif spec.get("npc") and not job.get("spoke_to_target"):
   objective="Speak with "+spec["npc"]
  elif spec.get("item") and spec["item"] not in c["characters"][c["active"]]["inventory"]:
   objective="Obtain "+spec["item"]
  else:
   objective="Return to Captain Rowan in the square"
  for entry in entries:
   if entry["kind"]=="guild":entry["objective"]=objective
 return entries

def guild_rank(c):
 count=c.get("guild_jobs_completed",0)
 return "Veteran" if count>=4 else "Trusted" if count>=2 else "Novice"
def available_jobs(c):
 count=c.get("guild_jobs_completed",0)
 return [name for name,spec in JOBS.items() if count>=spec.get("requires_jobs",0)]
