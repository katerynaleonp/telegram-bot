from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GOOGLE_SCRIPT_URL = os.environ.get("GOOGLE_SCRIPT_URL")

user_data = {}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

def save_to_google_sheets(chat_id, state, final_text):
    if not GOOGLE_SCRIPT_URL:
        return

    payload = {
        "telegram_id": chat_id,
        "name": state.get("name", ""),
        "phone": state.get("phone", ""),
        "text": final_text
    }

    try:
        requests.post(GOOGLE_SCRIPT_URL, json=payload)
    except:
        pass

@app.route('/', methods=['GET'])
def home():
    return "OK"

@app.route('/', methods=['POST'])
def webhook():
    data = request.json

    if not data or "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if chat_id not in user_data:
        user_data[chat_id] = {}

    state = user_data[chat_id]

    if text == "/start":
        send_message(chat_id, "Напишіть ваше ім'я")
        state["step"] = "name"
        return "ok"

    if state.get("step") == "name":
        state["name"] = text
        state["step"] = "phone"
        send_message(chat_id, "Ваш телефон")
        return "ok"

    if state.get("step") == "phone":
        state["phone"] = text
        save_to_google_sheets(chat_id, state, "Заявка")
        send_message(chat_id, "Дякуємо! 💛")
        user_data[chat_id] = {}
        return "ok"

    return "ok"
