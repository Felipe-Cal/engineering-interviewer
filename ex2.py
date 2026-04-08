import json

with open('data/data2.json', 'r') as f:
    data = json.load(f)

#print(json.dumps(data, indent=4))

p = {}
for sp in data['sprints']:
    team = sp['team']
    
    if team not in p:
        p[team] = []
        
    p[team].append({
        "sprint": sp['sprint'],
        "comp_rate": round(sp['completed'] / sp['planned'], 2),
        "carried_rate": round(sp['carried_over'] / sp['planned'], 2),
        "bugs": sp['bugs_filed'],
        "avg_bugs": round(sp['bugs_filed']*sp['completed'] / sp['planned'], 2)
    })

print(json.dumps(p, indent=4))