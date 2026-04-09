from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GOOGLE_SCRIPT_URL = os.environ.get("GOOGLE_SCRIPT_URL")


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


def send_to_google_sheets(name, phone):
    try:
        data = {
            "name": name,
            "phone": phone
        }
        requests.post(GOOGLE_SCRIPT_URL, json=data)
    except:
        pass


user_data = {}


@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    if not data or "message" not in data:
        return "ok"

    chat_id = str(data["message"]["chat"]["id"])
    text = data["message"].get("text", "")

    if chat_id not in user_data:
        user_data[chat_id] = {"step": "name"}

    step = user_data[chat_id]["step"]

    # КРОК 1 — ім’я
    if step == "name":
        user_data[chat_id]["name"] = text
        user_data[chat_id]["step"] = "phone"
        send_message(chat_id, "Залиште, будь ласка, Ваш номер телефону 📞")
        return "ok"

    # КРОК 2 — телефон
    if step == "phone":
        user_data[chat_id]["phone"] = text

        name = user_data[chat_id]["name"]
        phone = user_data[chat_id]["phone"]

        send_to_google_sheets(name, phone)

        send_message(chat_id, "Дякуємо! Ми зв’яжемося з вами ❤️")

        user_data[chat_id] = {"step": "name"}
        return "ok"

    return "ok"


@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"
