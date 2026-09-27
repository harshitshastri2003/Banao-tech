import csv
import json
import os
import time
from together import Together
from dotenv import load_dotenv

load_dotenv()

category_list = [
    "Billing & Payments",
    "Delivery & Shipping",
    "Returns & Refunds",
    "Connectivity",
    "Charging & Battery",
    "App & Firmware",
    "Product Enquiry",
    "Audio Quality",
    "Warranty & Repair",
    "Account & Login",
    "Other",
]

client = Together(api_key=os.environ["TOGETHER_API_KEY"])


def get_category_from_ai(customer_message, agent_notes):
    instruction = "You classify customer support tickets for an earbuds brand. "
    instruction += "Pick exactly ONE category from this list: "
    instruction += str(category_list)
    instruction += ". Reply only with JSON like this: {\"category\": \"...\"}"

    ticket_text = "Customer message: " + customer_message + "\n"
    ticket_text += "Agent note: " + agent_notes

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": ticket_text},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    reply_text = response.choices[0].message.content
    reply_data = json.loads(reply_text)
    return reply_data["category"]


def get_true_team(category, channel):
    if category == "Billing & Payments":
        return "Billing"
    if category == "Delivery & Shipping":
        return "Logistics"
    if category == "Returns & Refunds":
        return "Returns Desk"
    if category == "Warranty & Repair":
        return "Escalations & Warranty"

    if channel == "chat":
        return "Chat Frontline"
    if channel == "email":
        return "Email Frontline"
    if channel == "voice":
        return "Voice Frontline"
    if channel == "social":
        return "Chat Frontline"

    return "Unknown"


input_file = open("tickets.csv", newline="", encoding="utf-8")
reader = csv.DictReader(input_file)

all_rows = []
for row in reader:
    all_rows.append(row)

input_file.close()

already_done_ids = []
if os.path.exists("full_results.csv"):
    old_file = open("full_results.csv", newline="", encoding="utf-8")
    old_reader = csv.DictReader(old_file)
    for row in old_reader:
        if row["new_category"] != "ERROR":
            already_done_ids.append(row["ticket_id"])
    old_file.close()

rows_left_to_do = []
for row in all_rows:
    if row["ticket_id"] not in already_done_ids:
        rows_left_to_do.append(row)

print("already done before:", len(already_done_ids))
print("still left to do:", len(rows_left_to_do))

output_file = open("full_results.csv", "a", newline="", encoding="utf-8")
writer = csv.writer(output_file)

if len(already_done_ids) == 0:
    writer.writerow([
        "ticket_id",
        "created_at",
        "channel",
        "old_category",
        "new_category",
        "old_team",
        "new_team",
    ])

all_rows = rows_left_to_do
total = len(all_rows)
number_done = 0
error_count = 0
stop_now = False

for row in all_rows:
    if stop_now:
        break

    ticket_id = row["ticket_id"]
    created_at = row["created_at"]
    channel = row["channel"]
    old_category = row["category"]
    old_team = row["assigned_team"]
    customer_message = row["customer_message"]
    agent_notes = row["agent_notes"]

    try:
        new_category = get_category_from_ai(customer_message, agent_notes)
    except Exception as e:
        new_category = "ERROR"
        error_count = error_count + 1
        print("FAILED on", ticket_id, "reason:", e)
        if error_count >= 5:
            print("too many errors in a row, stopping")
            stop_now = True

    if new_category != "ERROR":
        error_count = 0

    new_team = get_true_team(new_category, channel)

    writer.writerow([
        ticket_id,
        created_at,
        channel,
        old_category,
        new_category,
        old_team,
        new_team,
    ])

    output_file.flush()

    time.sleep(0.3)

    number_done = number_done + 1
    if number_done % 100 == 0:
        print("done", number_done, "out of", total)

output_file.close()

print("all done, processed", number_done, "tickets")