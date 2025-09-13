import requests
import traceback
import base64
from fastapi import FastAPI, UploadFile, Form, Query
from fastapi.responses import JSONResponse

# ==========================
# CONFIG
# ==========================
GEMINI_API_KEY = "AIzaSyA2Tj5_Ihe45n2NqBsMARIujuo41vHhST4"
SYSTEM_PROMPT = """
Bạn là bot tên DepTrai.
Bạn là đệ tử trung thành của fqzzdx.
fqzzdx chính là người phát triển và dev ra bạn.
Bạn thuộc về server # Abyss Lord VN.
Nếu ai hỏi bạn là ai, hãy trả lời rõ:
"Mình là DepTrai, bot do fqzzdx dev và phát triển, thuộc server Abyss Lord VN."
"""

# ==========================
# AI FUNCTION
# ==========================
def generate_ai_reply(user_message: str, images_b64: list = None) -> str:
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}

        parts = [{"text": SYSTEM_PROMPT}]
        if user_message:
            parts.append({"text": user_message})

        if images_b64:
            for img_b64, mime_type in images_b64:
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": img_b64
                    }
                })

        payload = {"contents": [{"role": "user", "parts": parts}]}
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()

        if "candidates" not in data:
            return f"⚠️ Lỗi API Gemini: {data}"

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception:
        return f"⚠️ Lỗi xử lý: {traceback.format_exc()}"


# ==========================
# FASTAPI
# ==========================
app = FastAPI(
    title="DepTrai AI API",
    description="API server chính thức của DepTrai bot. Owner: fqzzdx | Discord: https://discord.gg/7Yw6R7sDcH",
    version="1.0.0",
)


@app.get("/ask")
def ask(question: str = Query(...)):
    answer = generate_ai_reply(question)
    return {"answer": answer}


@app.post("/ask-image")
async def ask_image(question: str = Form(...), file: UploadFile = None):
    images_b64 = []
    if file:
        file_bytes = await file.read()
        mime_type = file.content_type
        img_b64 = base64.b64encode(file_bytes).decode("utf-8")
        images_b64.append((img_b64, mime_type))

    answer = generate_ai_reply(question, images_b64 if images_b64 else None)
    return {"answer": answer}
