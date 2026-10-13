"""Party commands that operate only on existing campaign members."""
import re

def choose(campaign, name):
    if not campaign.get("started"):raise ValueError("Start the campaign first.")
    if not campaign.get("characters"):raise ValueError("There are no party members.")
    wanted=str(name).strip().casefold()
    matches=[i for i,h in enumerate(campaign["characters"]) if h["name"].casefold()==wanted]
    if len(matches)!=1:raise ValueError("Select a unique existing party member.")
    campaign["active"]=matches[0]
    hero=campaign["characters"][matches[0]]
    message=f"{hero['name']} is now the active adventurer."
    campaign["history"].append(message)
    return message
def parse(text):
    expression=r'^(?:i\s+)?(?:want to |would like to |please )?(?:switch to|select|control|play as|change character to)\s+(.+?)[.!]?$'
    match=re.fullmatch(expression,str(text).casefold().strip())
    return match.group(1).strip() if match else None
