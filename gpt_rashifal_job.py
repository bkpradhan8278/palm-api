import os
import openai
from datetime import datetime, timedelta
from firebase_admin import firestore, initialize_app

# Initialize Firebase
initialize_app()
db = firestore.client()

openai.api_key = os.getenv("OPENAI_API_KEY")

rashis = [
    "Mesh", "Vrishabha", "Mithun", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"
]

def get_gpt_rashifal(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def save_rashifal_to_firestore(collection, date_key, data):
    doc_ref = db.collection(collection).document(date_key)
    doc_ref.set(data)
    print(f"✅ {collection} written for {date_key}")

def run_daily_rashifal():
    today = datetime.now().strftime("%Y-%m-%d")
    data = {}
    for rashi in rashis:
        prompt = f"Give a short poetic DAILY horoscope in Hindi and English for zodiac sign '{rashi}'. Format as: ENGLISH:..., HINDI:..."
        prediction = get_gpt_rashifal(prompt)
        try:
            en, hi = prediction.split("HINDI:")
            data[rashi] = {
                "en": en.replace("ENGLISH:", "").strip(),
                "hi": hi.strip(),
                "timestamp": firestore.SERVER_TIMESTAMP
            }
        except Exception as e:
            print(f"❌ Parsing failed for {rashi}: {prediction}")
    save_rashifal_to_firestore("rashifal_daily", today, data)

def run_weekly_rashifal():
    # Always use this week's Monday as the doc key
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    week_key = monday.strftime("%Y-%m-%d")
    data = {}
    for rashi in rashis:
        prompt = f"Give a short 3-point WEEKLY horoscope in Hindi and English for zodiac sign '{rashi}' for this week. Add a lucky tip. Format as: ENGLISH:..., HINDI:..."
        prediction = get_gpt_rashifal(prompt)
        try:
            en, hi = prediction.split("HINDI:")
            data[rashi] = {
                "en": en.replace("ENGLISH:", "").strip(),
                "hi": hi.strip(),
                "timestamp": firestore.SERVER_TIMESTAMP
            }
        except Exception as e:
            print(f"❌ Parsing failed for {rashi}: {prediction}")
    save_rashifal_to_firestore("rashifal_weekly", week_key, data)

if __name__ == "__main__":
    import sys
    mode = "both" if len(sys.argv) == 1 else sys.argv[1]
    if mode in ("daily", "both"):
        run_daily_rashifal()
    if mode in ("weekly", "both"):
        # Only run weekly on Mondays!
        today = datetime.now()
        if today.weekday() == 0 or mode == "weekly":
            run_weekly_rashifal()
