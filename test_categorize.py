import csv
import json
import os
import random
import time
from groq import Groq
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

api_key = os.environ["GROQ_API_KEY"]
client = Groq(api_key=api_key)


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


def main():
    input_file = open("tickets.csv", newline="", encoding="utf-8")
    reader = csv.DictReader(input_file)

    all_rows = []
    for row in reader:
        all_rows.append(row)

    input_file.close()

    random.seed(1)
    sample_rows = random.sample(all_rows, 100)

    output_file = open("results.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(output_file)
    writer.writerow(["ticket_id", "old_category", "new_category", "match"])

    changed_count = 0
    same_count = 0

    number_done = 0
    for row in sample_rows:
        ticket_id = row["ticket_id"]
        old_category = row["category"]
        customer_message = row["customer_message"]
        agent_notes = row["agent_notes"]

        new_category = get_category_from_ai(customer_message, agent_notes)

        if old_category == new_category:
            match = "SAME"
            same_count = same_count + 1
        else:
            match = "CHANGED"
            changed_count = changed_count + 1

        writer.writerow([ticket_id, old_category, new_category, match])

        number_done = number_done + 1
        print("done", number_done, "out of 100")

    output_file.close()

    print("")
    print("SAME:", same_count)
    print("CHANGED:", changed_count)


main()