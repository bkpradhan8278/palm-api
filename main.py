from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import mediapipe as mp
import requests
import openai

# Roboflow API details (replace with your actual values)
ROBOFLOW_API_URL = "YOUR_ROBOFLOW_API_URL"
ROBOFLOW_API_KEY = "YOUR_ROBOFLOW_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

app = FastAPI()
mp_hands = mp.solutions.hands

class PalmRequest(BaseModel):
    image: str  # base64 string

def get_palm_lines(base64_img):
    headers = {'Authorization': f'Bearer {ROBOFLOW_API_KEY}'}
    payload = {'image': base64_img}
    response = requests.post(ROBOFLOW_API_URL, json=payload, headers=headers)
    if response.ok:
        return response.json()
    else:
        return {"error": response.text}

def generate_gpt_report(landmarks, palm_lines):
    openai.api_key = OPENAI_API_KEY
    prompt = f"""
    Analyze this palm:
    Landmark coordinates: {landmarks}
    Palm line features: {palm_lines}
    Give a detailed palmistry report including personality, life, career, and relationship aspects.
    """
    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a palmistry expert AI."},
                  {"role": "user", "content": prompt}]
    )
    return completion['choices'][0]['message']['content']

@app.post("/predict_palm")
async def predict_palm(request: PalmRequest):
    try:
        image_data = base64.b64decode(request.image)
        img = Image.open(BytesIO(image_data)).convert("RGB")
        img_np = np.array(img)

        # Step 1: MediaPipe for landmarks
        with mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5) as hands:
            results = hands.process(img_np)
            if not results.multi_hand_landmarks:
                return {"prediction": "No hand detected. Please upload a clear palm image."}
            hand_landmarks = results.multi_hand_landmarks[0]
            coords = [
                {"x": lm.x, "y": lm.y, "z": lm.z}
                for lm in hand_landmarks.landmark
            ]

        # Step 2: Roboflow for palm lines
        palm_lines_result = get_palm_lines(request.image)

        # Step 3: GPT for full report
        palm_lines_summary = palm_lines_result.get("predictions") or palm_lines_result.get("mask") or palm_lines_result
        final_report = generate_gpt_report(
            landmarks=coords,
            palm_lines=palm_lines_summary
        )

        return {"prediction": final_report}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
