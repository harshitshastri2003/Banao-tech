import csv
import json
import os
import random
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ["GROQ_API_KEY"]
client = Groq(api_key=api_key)


def get_summary_from_ai(customer_message, agent_notes):
    instruction = "Summarize this support ticket in 5 to 10 words only. "
    instruction += "Just the core issue, plain words, no extra explanation. "
    instruction += "Reply only with JSON like this: {\"summary\": \"...\"}"

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
    return reply_data["summary"]


results_file = open("results.csv", newline="", encoding="utf-8")
results_reader = csv.DictReader(results_file)

all_results = []
for row in results_reader:
    all_results.append(row)

results_file.close()

random.seed(2)
sample_results = random.sample(all_results, 20)

sample_ticket_ids = []
for row in sample_results:
    sample_ticket_ids.append(row["ticket_id"])

tickets_file = open("tickets.csv", newline="", encoding="utf-8")
tickets_reader = csv.DictReader(tickets_file)

ticket_text_lookup = {}
for row in tickets_reader:
    if row["ticket_id"] in sample_ticket_ids:
        ticket_text_lookup[row["ticket_id"]] = row

tickets_file.close()

output_file = open("manual_check_sample.csv", "w", newline="", encoding="utf-8")
writer = csv.writer(output_file)
writer.writerow(["ticket_id", "summary", "customer_message", "agent_notes", "old_category", "ai_category", "your_answer"])

number_done = 0
for row in sample_results:
    ticket_id = row["ticket_id"]
    old_category = row["old_category"]
    ai_category = row["new_category"]
    full_ticket = ticket_text_lookup[ticket_id]
    customer_message = full_ticket["customer_message"]
    agent_notes = full_ticket["agent_notes"]

    summary = get_summary_from_ai(customer_message, agent_notes)

    writer.writerow([ticket_id, summary, customer_message, agent_notes, old_category, ai_category, ""])

    number_done = number_done + 1
    print("done", number_done, "out of 20")

output_file.close()

print("done, check manual_check_sample.csv")