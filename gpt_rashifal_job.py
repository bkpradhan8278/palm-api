import os
import openai
from datetime import datetime, timedelta
from firebase_admin import credentials, firestore, initialize_app

# Firebase Admin initialization with Render secret file
cred = credentials.Certificate("serviceAccount")  # <-- Use the exact secret file name you set in Render
initialize_app(cred)
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

def parse_multilang_prediction(prediction):
    """
    Expects: ENGLISH: ... HINDI: ... ODIA: ...
    Returns: en, hi, or
    """
    try:
        en = prediction.split("ENGLISH:")[1].split("HINDI:")[0].strip()
        hi = prediction.split("HINDI:")[1].split("ODIA:")[0].strip()
        or_ = prediction.split("ODIA:")[1].strip()
        return en, hi, or_
    except Exception as e:
        print(f"❌ Multi-lang parsing failed: {prediction}")
        return prediction, "", ""

def save_rashifal_to_firestore(collection, date_key, data):
    doc_ref = db.collection(collection).document(date_key)
    doc_ref.set(data)
    print(f"✅ {collection} written for {date_key}")

def run_daily_rashifal():
    today = datetime.now().strftime("%Y-%m-%d")
    data = {}
    for rashi in rashis:
        prompt = (
            f"Give a short poetic DAILY horoscope for zodiac sign '{rashi}' in three languages. "
            f"Format as: ENGLISH:..., HINDI:..., ODIA:..."
        )
        prediction = get_gpt_rashifal(prompt)
        en, hi, or_ = parse_multilang_prediction(prediction)
        data[rashi] = {
            "en": en,
            "hi": hi,
            "or": or_,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
    save_rashifal_to_firestore("rashifal_daily", today, data)

def run_weekly_rashifal():
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    week_key = monday.strftime("%Y-%m-%d")
    data = {}
    for rashi in rashis:
        prompt = (
            f"Give a short 3-point WEEKLY horoscope for zodiac sign '{rashi}' for this week in three languages and add a lucky tip. "
            f"Format as: ENGLISH:..., HINDI:..., ODIA:..."
        )
        prediction = get_gpt_rashifal(prompt)
        en, hi, or_ = parse_multilang_prediction(prediction)
        data[rashi] = {
            "en": en,
            "hi": hi,
            "or": or_,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
    save_rashifal_to_firestore("rashifal_weekly", week_key, data)

if __name__ == "__main__":
    import sys
    mode = "both" if len(sys.argv) == 1 else sys.argv[1]
    if mode in ("daily", "both"):
        run_daily_rashifal()
    if mode in ("weekly", "both"):
        today = datetime.now()
        if today.weekday() == 0 or mode == "weekly":
            run_weekly_rashifal()
