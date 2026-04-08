import json
import statistics
from datetime import datetime

with open('data/data.json', 'r') as f:
    data = json.load(f)


total_runs = 0
total_pass = 0

for d in data['pipelines']:
    total_runs += d['total_runs']
    total_pass += d['passed']


average_pass_rate = total_pass / total_runs * 100
print(f'Pass rate: {average_pass_rate:.2f}%')

week_pass_rate = []
for d in data['pipelines']:
    rate = (d['passed'] / d['total_runs'] * 100)
    week_pass_rate.append([d['week'], round(rate, 2), d['avg_duration_min'], d['top_failure_stage']])

print(f"Weekly pass rate: {week_pass_rate}")

under_performed_weeks = []
for w in week_pass_rate:
    if w[1] < average_pass_rate:
        #week_date = datetime.strptime(f"2024-{w[0]}-1", "%G-W%V-%u")
        #under_performed_weeks.append([week_date.strftime("%m/%d"), w[1]])
        under_performed_weeks.append(w[0])

print(f"Under performed weeks: {under_performed_weeks}")


flag_rate = 0
incidents_weeks = []
for inc in data['incidents']:
    incidents_weeks.append([inc['week'], inc['preceded_by_pipeline_failures']])
    if inc['preceded_by_pipeline_failures']:
        flag_rate += 1

print(f"Flag rate: {flag_rate / len(data['incidents']) * 100:.2f}%")
print(f"Incidents weeks: {incidents_weeks}")

for w in incidents_weeks:
    if w[0] in under_performed_weeks:
        print(f"Incident week {w[0]} is under performing. Preceded by pipeline failures: {w[1]}")
    else:
        print(f"Incident week {w[0]} is not under performing. Preceded by piepline failures: {w[1]}")