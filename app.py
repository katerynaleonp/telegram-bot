from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GOOGLE_SCRIPT_URL = os.environ.get("GOOGLE_SCRIPT_URL")

user_data = {}

BTN_QUESTION = "Задати питання"
BTN_MANAGER = "Написати менеджеру"
BTN_CALLBACK = "Замовити зворотний зв'язок"


def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        payload["reply_markup"] = keyboard

    requests.post(url, json=payload)


def show_main_menu(chat_id):
    keyboard = {
        "keyboard": [
            [{"text": BTN_QUESTION}],
            [{"text": BTN_MANAGER}],
            [{"text": BTN_CALLBACK}]
        ],
        "resize_keyboard": True
    }

    send_message(chat_id, "Вітаємо! Оберіть, будь ласка, що Вас цікавить:", keyboard)


def send_to_google_sheets(chat_id, state, final_text):
    try:
        data = {
            "telegram_id": chat_id,
            "username": state.get("username", ""),
            "request_type": state.get("request_type", ""),
            "parent_name": state.get("name", ""),
            "phone": state.get("phone", ""),
            "student_name": "",
            "age": "",
            "final_text": final_text
        }
        requests.post(GOOGLE_SCRIPT_URL, json=data, timeout=10)
    except:
        pass


@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    if not data or "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = str(message["chat"]["id"])
    text = message.get("text", "")
    username = message.get("from", {}).get("username", "")

    if chat_id not in user_data:
        user_data[chat_id] = {}

    state = user_data[chat_id]

    if text == "/start":
        user_data[chat_id] = {}
        show_main_menu(chat_id)
        return "ok"

    if text == BTN_QUESTION:
        user_data[chat_id] = {
            "step": "name",
            "request_type": BTN_QUESTION,
            "username": username
        }
        send_message(chat_id, "Напишіть, будь ласка, Ваше ім'я 😊")
        return "ok"

    if text == BTN_MANAGER:
        user_data[chat_id] = {
            "step": "name",
            "request_type": BTN_MANAGER,
            "username": username
        }
        send_message(chat_id, "Напишіть, будь ласка, Ваше ім'я 😊")
        return "ok"

    if text == BTN_CALLBACK:
        user_data[chat_id] = {
            "step": "name",
            "request_type": BTN_CALLBACK,
            "username": username
        }
        send_message(chat_id, "Напишіть, будь ласка, Ваше ім'я 😊")
        return "ok"

    if not state.get("step"):
        show_main_menu(chat_id)
        return "ok"

    if state["step"] == "name":
        state["name"] = text
        state["step"] = "phone"
        send_message(chat_id, "Залиште, будь ласка, Ваш номер телефону 📞")
        return "ok"

    if state["step"] == "phone":
        state["phone"] = text

        if state["request_type"] == BTN_QUESTION:
            state["step"] = "final_question"
            send_message(chat_id, "Залиште, будь ласка, Ваше питання")
            return "ok"

        if state["request_type"] == BTN_MANAGER:
            state["step"] = "final_message"
            send_message(chat_id, "Залиште, будь ласка, Ваше повідомлення")
            return "ok"

        if state["request_type"] == BTN_CALLBACK:
            send_to_google_sheets(chat_id, state, "Запит на зворотний зв'язок")
            send_message(chat_id, "Дякуємо! Ми зв’яжемося з вами ❤️")
            user_data[chat_id] = {}
            return "ok"

    if state["step"] == "final_question":
        final_text = text
        send_to_google_sheets(chat_id, state, final_text)
        send_message(chat_id, "Дякуємо! Ми зв’яжемося з вами ❤️")
        user_data[chat_id] = {}
        return "ok"

    if state["step"] == "final_message":
        final_text = text
        send_to_google_sheets(chat_id, state, final_text)
        send_message(chat_id, "Дякуємо! Ми зв’яжемося з вами ❤️")
        user_data[chat_id] = {}
        return "ok"

    return "ok"


@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"
