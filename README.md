# Vireo Audio Ticket Categorizer

When a customer messages Vireo Audio's support team, a chatbot quickly guesses what the problem is about (like "Billing" or "Delivery") and tags the ticket with that guess. Agents can fix this tag later, but in practice they almost never do.

This project checks: are these tags actually correct? And if not, can an AI read the ticket properly and fix them? The goal is to find out which support team is really doing the most work, so the company can decide where to hire.

## How to run this on your own computer

1. Install Python (version 3.10 or newer).

2. Open this folder in a terminal. Create a virtual environment (a separate, clean space just for this project's packages):
   python -m venv venv

3. Activate it:
   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - Mac/Linux: `source venv/bin/activate`
4. Install packages:
   pip install groq python-dotenv


5. Get a free API key from console.groq.com. Create a file named `.env` in this folder with:
   GROQ_API_KEY=your-key-here

6. Place `tickets.csv` in this same folder (not included in this repo, see note below).
7. Run:
   python full_run.py

This calls the AI once per ticket (~11,780 tickets), so it takes a few hours. Progress saves after every single ticket into `full_results.csv`, so you can check on it anytime.



## What we actually built

- A script that re-reads every ticket's customer message and agent note, and picks the correct category out of the same 11 labels the company already uses
- A team-routing rule (same logic the company already applies, just fed the corrected category instead of the chatbot's guess)
- A manual validation step on 20 random tickets, checked by hand, comparing the old label vs the AI's label against our own read of each ticket
- Result: old tags matched our own judgment 55% of the time. The AI's re-categorization matched 85% of the time.
- - Ran the categorizer on 6,087 tickets (Jan 2025–Nov 2025, ~52% of the full dataset)



## What we considered and did not build, and why

- **A caching layer for exact-duplicate ticket text.** Checked the actual data first: zero exact duplicates exist across all 11,780 tickets (every message has its own order number, name, phrasing). Left the logic in since it's harmless, but it never actually triggers on this dataset.
- **A frontend/dashboard.** The brief doesn't ask for one, and "a small thing that runs beats a large thing that does not." A script + a chart answers the actual business question without burning hours on something nobody asked for.
- **Separate handling for voice ticket transcripts.** Voice tickets come in as IVR transcripts, not the customer's own words, which could affect accuracy slightly differently than chat/email. We didn't build special-case logic for this given the time cap; it's a known limitation, not an oversight.
- **A resumable/checkpointed run.** If `full_run.py` crashes partway, it currently has to restart from ticket 1. Given the ~5 hour effort cap, we accepted this risk rather than build a resume feature, since the run itself doesn't count against that cap.


## Output

`full_results.csv` contains, for every ticket:
- `old_category` — what it started with
- `new_category` — what the AI decided after actually reading it
- `old_team` — who it was originally routed to
- `new_team` — who it should have actually gone to


## Other scripts in this folder

- `test_categorize.py` — quick test run on 100 random tickets, used before committing to the full run
- `pick_sample.py` — pulls 20 random tickets with a short AI-written summary, for manual accuracy checking

## A note on how the full run actually went

We started on Groq's free tier. It hit a hard daily limit (200,000 tokens/day for this model) after about 2,500 tickets. Rather than stop there, we added billing to Together.ai and used it to process the remaining tickets, since Groq's paid tier was closed for new signups at the time. In total we categorized **6,087 tickets — about 52% of the full dataset**, covering January 2025 through November 2025. We ran out of processing time before reaching December 2025 onward, due to a mix of rate limits and a couple of provider outages along the way.


