import csv
import matplotlib.pyplot as plt

input_file = open("full_results.csv", newline="", encoding="utf-8")
reader = csv.DictReader(input_file)

team_counts = {}
category_counts = {}
all_months = []
all_teams = []
all_categories = []

for row in reader:
    created_at = row["created_at"]
    month = created_at[0:7]

    if month < "2025-01":
        continue

    if row["new_category"] == "ERROR":
        continue

    team = row["new_team"]
    category = row["new_category"]

    if month not in all_months:
        all_months.append(month)
    if team not in all_teams:
        all_teams.append(team)
    if category not in all_categories:
        all_categories.append(category)

    team_key = month + "|" + team
    if team_key in team_counts:
        team_counts[team_key] = team_counts[team_key] + 1
    else:
        team_counts[team_key] = 1

    category_key = month + "|" + category
    if category_key in category_counts:
        category_counts[category_key] = category_counts[category_key] + 1
    else:
        category_counts[category_key] = 1

input_file.close()

all_months.sort()


def make_stacked_chart(counts, group_list, title, filename):
    plt.figure()
    bottom_so_far = [0] * len(all_months)

    for group in group_list:
        values = []
        for month in all_months:
            key = month + "|" + group
            if key in counts:
                values.append(counts[key])
            else:
                values.append(0)

        plt.bar(all_months, values, bottom=bottom_so_far, label=group)

        index = 0
        for v in values:
            bottom_so_far[index] = bottom_so_far[index] + v
            index = index + 1

    plt.xlabel("Month")
    plt.ylabel("Number of tickets")
    plt.title(title)
    plt.xticks(rotation=90)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(filename)


make_stacked_chart(team_counts, all_teams, "Tickets per month, by team (corrected)", "chart_by_team.png")
make_stacked_chart(category_counts, all_categories, "Tickets per month, by category (corrected)", "chart_by_category.png")

print("done, check chart_by_team.png and chart_by_category.png")