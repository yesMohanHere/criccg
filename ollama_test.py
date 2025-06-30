# # import requests

# # commentary = [
# #     "What a delivery! Clean bowled.",
# #     "He pulls that for a boundary.",
# #     "No ball signaled by the umpire.",
# #     "Drinks break now.",
# #     "That's high and handsome – SIX!"
# # ]

# # prompt = f"""Label the following cricket commentary with one of these: [SIX, FOUR, WICKET, LBW, EXTRA, BREAK, OTHER].

# # Commentary: "{commentary}"

# # Just respond with the label only."""

# # response = requests.post(
# #     "http://localhost:11434/api/generate",
# #     json={
# #         "model": "deepseek-r1:7b",
# #         "prompt": prompt,
# #         "stream": False
# #     }
# # )

# # label = response.json()["response"].strip()
# # print(f"📄 Commentary: {commentary}")
# # print(f"📌 Predicted Label: {label}")

# #####################################################################################################
# # import json
# # import requests
# # import time

# # # Load cleaned transcript
# # with open(r"C:\Users\HILCPS\Downloads\transcript_clean.json", "r", encoding="utf-8") as f:
# #     transcript = json.load(f)

# # labeled_transcript = []

# # # Loop through each line and send to Ollama
# # for i, item in enumerate(transcript):
# #     text = item["text"]
# #     #prompt = f'Label the following cricket commentary: "{text}"'
# #     prompt = (
# #     f"Label the following cricket commentary into one word from this list:\n"
# #     f"['SIX', 'FOUR', 'WICKET','LBW', 'BREAK', 'EXTRA', 'DOT BALL','SINGLE', 'DOUBLE','RUN OUT','WIDE','STRATEGY BREAK', 'COMMENTARY', 'UNKNOWN'].\n"
# #     f"Only reply with one of the labels.\n\n"
# #     f"Commentary: \"{text}\""
# # )


# #     try:
# #         response = requests.post(
# #             "http://localhost:11434/api/generate",
# #             json={
# #                 "model": "deepseek-r1:32b",  # or any model you’ve listed
# #                 "prompt": prompt,
# #                 "stream": False
# #             }
# #         )
# #         label = response.json()["response"].strip()

# #         # Append labeled entry
# #         labeled_transcript.append({
# #             "start": item["start"],
# #             "end": item["end"],
# #             "text": text,
# #             "label": label
# #         })

# #         print(f"[{i+1}/{len(transcript)}] {label} <- {text}")

# #         time.sleep(1)  # Small delay to avoid overloading
# #     except Exception as e:
# #         print(f"Error labeling: {text}\n{e}")
# #         continue

# # # Save labeled transcript
# # with open(r"C:\Users\HILCPS\Downloads\transcript_labeled.json", "w", encoding="utf-8") as f:
# #     json.dump(labeled_transcript, f, indent=4, ensure_ascii=False)

# # print("\n✅ Labeled transcript saved as transcript_labeled.json")

# ###############################################################################################
import json
import requests
import time

# Predefined labels (strict filter)

VALID_LABELS = [
    'SIX',              # Six runs
    'FOUR',             # Four runs
    'WICKET',           # Generic dismissal
    'LBW',              # Leg Before Wicket
    'RUN OUT',          # Run out dismissal
    'WIDE',             # Wide delivery
    'NO BALL',          # No ball delivery
    'FREE HIT',         # Free hit after no ball
    'EXTRA',            # Byes, Leg Byes, Wides, etc. (excluding NO BALL now)
    'DOT BALL',         # No run scored
    'SINGLE',           # 1 run
    'DOUBLE',           # 2 runs
    'THREE',            # 3 runs
    'BREAK',            # Non-strategy pause (injury, drinks, etc.)
    'STRATEGY BREAK',   # Timeouts like Strategic Timeout or Innings Break
    'COMMENTARY',       # General chatter (e.g., insights, trivia, mood)
    'SCORE UPDATE',     # Commentary with current score info
    'UNKNOWN',          # For ambiguous or unclear commentary

    # Event-related
    'APPEAL',           # Player appeal but not clearly a dismissal yet
    'MISS',             # Batter missed the ball completely
    'EDGE',             # Bat-edge mentioned (nick, edge)
    'REVIEW',           # Mentions or request for review/DRS
    'FIELDING EFFORT',  # Fielding actions that don't cause dismissal
    'DROPPED CATCH',    # Catch opportunity missed
    'BALL CONTACT',     # Ball hits bat/pad/body/ground but no clear outcome

    # Informational
    'MILESTONE',             # 50/100 runs by player or team
    'BOWLING CHANGE',        # Change in bowler
    'CAPTAINCY DECISION',    # Field change, bowling choice, etc.
    'INJURY',                # Player injury
    'PLAYER INTRO',          # New batsman or bowler intro
    'WEATHER INTERRUPTION'   # Rain, light, etc.
]


# Load cleaned transcript
with open(r"C:\Users\HILCPS\Downloads\transcript_clean_p8209.json", "r", encoding="utf-8") as f:
    transcript = json.load(f)

labeled_transcript = []

# Loop through each line and send to Ollama
for i, item in enumerate(transcript):
    text = item["text"]
    # previous_line = transcript[i - 1]["text"] if i > 0 else ""
    # next_line = transcript[i + 1]["text"] if i < len(transcript) - 1 else ""
    prompt = (
        f"You are a cricket commentary classification assistant.\n\n"
        f"Label the following cricket commentary into one word from this list:\n"
        f"{list(VALID_LABELS)}.\n"
        f"Only reply with one of the labels exactly as it appears in the list.\n\n"
        f"- Focus on the 'Target Commentary' line. Use context only to disambiguate meaning if necessary apply some sentiment analysis to predict the labels.\n"
        f"Commentary: \"{text}\""
    )
    # prompt = (
    #     f"You are a cricket commentary classification assistant.\n\n"
    #     f"Given a line of cricket commentary (with optional context), classify the target line using exactly **one label** from the following list:\n\n"
    #     f"{VALID_LABELS}\n\n"
    #     f"Instructions:\n"
    #     f"- Only respond with **one label**, exactly as written in the list above.\n"
    #     f"- Focus on the 'Target Commentary' line. Use context only to disambiguate meaning.\n"
    #     f"- Do not explain your answer. Just return the label.\n\n"
    #     f"Context Before: \"{previous_line}\"\n"
    #     f"Target Commentary: \"{text}\"\n"
    #     f"Context After: \"{next_line}\""
    # )


    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
               # "model": "deepseek-r1:32b",
                "model": "llama3.3:latest",
                
                "prompt": prompt,
                "stream": False
            }
        )
        raw_label = response.json()["response"].strip().upper()

        # Extract only valid label
        label = next((lbl for lbl in VALID_LABELS if lbl in raw_label.split()), "UNKNOWN")

        # Append labeled entry
        labeled_transcript.append({
            "start": item["start"],
            "end": item["end"],
            "text": text,
            "label": label
        })

        print(f"[{i+1}/{len(transcript)}] {label} <- {text}")

        time.sleep(1)  # Delay to avoid overloading
    except Exception as e:
        print(f"Error labeling: {text}\n{e}")
        continue

# Save to JSON
with open(r"C:\Users\HILCPS\Downloads\transcript_promptsenti_llama3_labels_p8209.json", "w", encoding="utf-8") as f:
    json.dump(labeled_transcript, f, indent=4, ensure_ascii=False)

print("\n✅ Labeled transcript saved as transcript_promptsenti_llama3_labels_p8209.json")
import json
import csv

# Load labeled JSON
input_path = r"C:\Users\HILCPS\Downloads\transcript_promptsenti_llama3_labels_p8209.json"
output_path = r"C:\Users\HILCPS\Downloads\transcript_promptsenti_llama3_labels_p8209.csv"

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Write to CSV
with open(output_path, "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["start", "end", "text", "label"])
    writer.writeheader()
    for item in data:
        writer.writerow(item)

print("✅ CSV saved to:", output_path)
