from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from google.generativeai import GenerativeModel
import google.generativeai as genai
import base64
import os
from dotenv import load_dotenv

# ✅ Load .env and configure Gemini
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY", "").strip()
genai.configure(api_key=api_key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def guess_mime_type(filename: str) -> str:
    ext = os.path.splitext(filename)[-1].lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "image/jpeg")

@app.post("/chat")
async def chat(prompt: str = Form(...), image: UploadFile = File(None)):
    model = GenerativeModel(model_name="models/gemini-2.0-flash")

    if image:
        image_bytes = await image.read()
        mime_type = guess_mime_type(image.filename)
        encoded = base64.b64encode(image_bytes).decode("utf-8")

        response = model.generate_content([
            prompt,
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": encoded
                }
            }
        ])
    else:
        response = model.generate_content(prompt)

    return {"response": response.text}
