from fastapi import FastAPI
from pydantic import BaseModel
import base64
from io import BytesIO
from PIL import Image

app = FastAPI()

class PalmRequest(BaseModel):
    image: str  # base64 string

@app.post("/predict_palm")
async def predict_palm(request: PalmRequest):
    image_data = base64.b64decode(request.image)
    img = Image.open(BytesIO(image_data))
    # TODO: Run your AI/ML logic here
    prediction = "This is a demo palm reading result. (Replace with your AI logic)"
    return {"prediction": prediction}
