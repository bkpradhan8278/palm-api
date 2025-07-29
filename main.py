from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
from io import BytesIO
from PIL import Image, UnidentifiedImageError

app = FastAPI()

class PalmRequest(BaseModel):
    image: str

@app.post("/predict_palm")
async def predict_palm(request: PalmRequest):
    try:
        image_data = base64.b64decode(request.image)
        img = Image.open(BytesIO(image_data))
        # Insert your AI logic here
        prediction = "This is a demo palm reading result."
        return {"prediction": prediction}
    except (base64.binascii.Error, UnidentifiedImageError) as e:
        raise HTTPException(status_code=400, detail="Invalid image data.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
