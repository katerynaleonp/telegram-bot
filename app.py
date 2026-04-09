from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

user_data = {}

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        payload["reply_markup"] = keyboard

    requests.post(url, json=payload)


def main_menu(chat_id):
    keyboard = {
        "keyboard": [
            [{"text": "Задати питання"}],
            [{"text": "Написати менеджеру"}],
            [{"text": "Замовити зворотний зв'язок"}]
        ],
        "resize_keyboard": True
    }

    send_message(chat_id, "Вітаємо! Оберіть, будь ласка, що Вас цікавить:", keyboard)


@app.route('/', methods=['POST'])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if chat_id not in user_data:
        user_data[chat_id] = {}

    state = user_data[chat_id]

    if text == "/start":
        user_data[chat_id] = {}
        main_menu(chat_id)
        return "ok"

    if text == "Задати питання":
        state["type"] = "question"
        state["step"] = "name"
        send_message(chat_id, "Будь ласка, напишіть ім’я представника.")
        return "ok"

    if text == "Написати менеджеру":
        state["type"] = "manager"
        state["step"] = "name"
        send_message(chat_id, "Будь ласка, напишіть ім’я представника.")
        return "ok"

    if text == "Замовити зворотний зв'язок":
        state["type"] = "callback"
        state["step"] = "name"
        send_message(chat_id, "Будь ласка, напишіть ім’я представника.")
        return "ok"

    if state.get("step") == "name":
        state["name"] = text
        state["step"] = "phone"
        send_message(chat_id, "Будь ласка, залиште номер телефону.")
        return "ok"

    if state.get("step") == "phone":
        state["phone"] = text
        state["step"] = "student"
        send_message(chat_id, "Напишіть, будь ласка, ім’я дитини або учня.")
        return "ok"

    if state.get("step") == "student":
        state["student"] = text
        state["step"] = "age"
        send_message(chat_id, "Вкажіть, будь ласка, вік.")
        return "ok"

    if state.get("step") == "age":
        state["age"] = text

        if state["type"] == "question":
            state["step"] = "final"
            send_message(chat_id, "Залиште Ваше питання.")
            return "ok"

        if state["type"] == "manager":
            state["step"] = "final"
            send_message(chat_id, "Залиште Ваше повідомлення.")
            return "ok"

        if state["type"] == "callback":
            send_message(chat_id, "Дякуємо за звернення! 💛 Ми скоро зв’яжемося з Вами.")
            user_data[chat_id] = {}
            return "ok"

    if state.get("step") == "final":
        send_message(chat_id, "Дякуємо за звернення! 💛 Ми скоро зв’яжемося з Вами.")
        user_data[chat_id] = {}
        return "ok"

    return "ok"
