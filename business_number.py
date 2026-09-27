import csv

input_file = open("full_results.csv", newline="", encoding="utf-8")
reader = csv.DictReader(input_file)

old_team_counts = {}
new_team_counts = {}
total = 0

for row in reader:
    if row["new_category"] == "ERROR":
        continue

    total = total + 1

    old_team = row["old_team"]
    new_team = row["new_team"]

    if old_team in old_team_counts:
        old_team_counts[old_team] = old_team_counts[old_team] + 1
    else:
        old_team_counts[old_team] = 1

    if new_team in new_team_counts:
        new_team_counts[new_team] = new_team_counts[new_team] + 1
    else:
        new_team_counts[new_team] = 1

input_file.close()

print("total tickets checked:", total)
print("")
print("OLD team split (official numbers):")
for team in old_team_counts:
    percent = old_team_counts[team] / total * 100
    print(" ", team, "-", old_team_counts[team], "tickets -", round(percent, 1), "%")

print("")
print("NEW team split (corrected):")
for team in new_team_counts:
    percent = new_team_counts[team] / total * 100
    print(" ", team, "-", new_team_counts[team], "tickets -", round(percent, 1), "%")