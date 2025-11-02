# app.py
import os
from typing import List
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid
import os
from typing import List

from chatbot_model import ChatbotModel
from db import init_db, log_message, get_session_history
from faq_fallback import FAQFallback
import nltk
from nltk.tokenize import word_tokenize


from chatbot_model import ChatbotModel
from db import init_db, log_message, get_session_history
from faq_fallback import FAQFallback
import nltk
from nltk.tokenize import word_tokenize


nltk.download('punkt', quiet=True)


# Initialize
init_db()
model = ChatbotModel(model_name="microsoft/DialoGPT-medium")


# Example FAQ set
faqs = {
"What are your hours?": "We are available 24/7 for basic help. For phone support, our hours are 9am–6pm UTC.",
"How do I reset my password?": "To reset your password, go to Settings → Account → Reset Password and follow the instructions.",
"Where can I see pricing?": "You can view pricing on our Pricing page or contact sales at sales@example.com.",
}
faq = FAQFallback(faqs)


app = FastAPI()
BASE_DIR = os.path.dirname(__file__)


# simple templates and static mount (templates/index.html provided below)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# In-memory session context (for demo). In prod, store in Redis or DB.
SESSIONS = {}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
# assign session id if not present on client — the front-end should manage this
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat")
async def chat_api(request: Request):
    data = await request.json()
    session_id = data.get("session_id") or str(uuid.uuid4())
    user_text = data.get("message", "")


    # log user message
    log_message(session_id, "user", user_text)


    # update in-memory session
    history = SESSIONS.get(session_id, [])
    history.append({"role": "user", "text": user_text})


    # run FAQ fallback first
    faq_answer = faq.query(user_text)
    if faq_answer:
        bot_reply = faq_answer
    else:
    # generate reply from model
        bot_reply = model.generate(history)


    # log bot reply
    log_message(session_id, "bot", bot_reply)
    history.append({"role": "bot", "text": bot_reply})
    SESSIONS[session_id] = history


    return JSONResponse({"session_id": session_id, "reply": bot_reply})


@app.get("/api/logs/{session_id}")
async def get_logs(session_id: str):
    rows = get_session_history(session_id)
    return JSONResponse({"session_id": session_id, "history": [{"role": r[0], "message": r[1]} for r in rows]})


if __name__ == '__main__':
    import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)