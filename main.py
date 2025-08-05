from flask import Flask, request
import requests
import os

TOKEN = "7105294830:AAEeKiQSK5rbolMaaClo49l2Y1QotvhbwY8"
ADMIN_ID = 7210975276
COLLABS = ["Ehsan71ehsan", "Arman1372"]

API = f"https://api.telegram.org/bot{TOKEN}/"
app = Flask(__name__)
user_states = {}

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "callback_query" in data:
        cb = data["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        username = cb["from"]["username"]
        data_value = cb["data"]
        cb_id = cb["id"]

        if username in COLLABS and data_value in ["20 گیگ", "30 گیگ", "40 گیگ", "50 گیگ"]:
            user_states[chat_id] = {"step": "waiting_for_name", "volume": data_value}
            send(chat_id, "✍️ لطفاً نام سرویس را وارد کنید:")
            answer_callback(cb_id, f"{data_value} انتخاب شد.")

        elif username in COLLABS and data_value in ["موبایل صدف", "موبایل آرمان"]:
            if chat_id in user_states and user_states[chat_id].get("step") == "waiting_for_shop":
                name = user_states[chat_id]["name"]
                volume = user_states[chat_id]["volume"]
                shop = data_value

                summary = f"📥 سفارش جدید:\n👤 نام سرویس: {name}\n📦 حجم: {volume}\n🏪 فروشگاه: {shop}"
                send(ADMIN_ID, summary)
                send(chat_id, "✅ سفارش شما ارسال شد.")
                user_states.pop(chat_id, None)
                answer_callback(cb_id, f"{shop} انتخاب شد.")

        elif chat_id == ADMIN_ID:
            if data_value == "admin_msg1":
                send(ADMIN_ID, "📢 پیام آماده ۱ ارسال شد!")
                answer_callback(cb_id, "پیام آماده ۱ ارسال شد.")
            elif data_value == "admin_msg2":
                send(ADMIN_ID, "📢 پیام آماده ۲ ارسال شد!")
                answer_callback(cb_id, "پیام آماده ۲ ارسال شد.")
            elif data_value == "admin_send_user":
                send(ADMIN_ID, "لطفا آیدی عددی کاربر را با فرمت زیر وارد کنید:\n/send user_id پیام")
                answer_callback(cb_id, "لطفا آیدی کاربر را وارد کنید.")

        return "ok", 200

    msg = data.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "")
    username = msg.get("from", {}).get("username", "")

    if text == "/start":
        if username in COLLABS:
            show_volume_options(chat_id)
        elif chat_id == ADMIN_ID:
            send(chat_id, "🔐 پنل مدیریت فعال است.\nبرای نمایش منوی ادمین، دستور /admin را ارسال کنید.")
        else:
            send(chat_id, "⛔️ شما مجاز به استفاده از ربات نیستید.")

    elif username in COLLABS:
        state = user_states.get(chat_id)

        if state and state.get("step") == "waiting_for_name":
            user_states[chat_id]["name"] = text
            user_states[chat_id]["step"] = "waiting_for_shop"
            show_shop_options(chat_id)
        else:
            send(chat_id, "لطفاً از /start شروع کنید و مراحل را طی کنید.")

    elif text == "/admin" and chat_id == ADMIN_ID:
        admin_menu(chat_id)

    elif chat_id == ADMIN_ID and text.startswith("/send "):
        try:
            _, uid, *msg_parts = text.split()
            user_id = int(uid)
            final_msg = " ".join(msg_parts)
            send(user_id, f"📦 پیام ارسالی:\n{final_msg}")
            send(chat_id, "📤 پیام ارسال شد.")
        except:
            send(chat_id, "❌ فرمت صحیح:\n/send user_id پیام")

    return "ok", 200

def show_volume_options(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "20 گیگ - 1 ماه", "callback_data": "20 گیگ"}],
            [{"text": "30 گیگ - 1 ماه", "callback_data": "30 گیگ"}],
            [{"text": "40 گیگ - 1 ماه", "callback_data": "40 گیگ"}],
            [{"text": "50 گیگ - 1 ماه", "callback_data": "50 گیگ"}],
        ]
    }
    requests.post(API + "sendMessage", json={
        "chat_id": chat_id,
        "text": "لطفاً حجم موردنظر را انتخاب کنید:",
        "reply_markup": keyboard
    })

def show_shop_options(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "📱 موبایل صدف", "callback_data": "موبایل صدف"}],
            [{"text": "📲 موبایل آرمان", "callback_data": "موبایل آرمان"}],
        ]
    }
    requests.post(API + "sendMessage", json={
        "chat_id": chat_id,
        "text": "🏪 لطفاً فروشگاه مربوطه را انتخاب کنید:",
        "reply_markup": keyboard
    })

def admin_menu(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "ارسال پیام آماده ۱", "callback_data": "admin_msg1"}],
            [{"text": "ارسال پیام آماده ۲", "callback_data": "admin_msg2"}],
            [{"text": "ارسال پیام به کاربر با آیدی", "callback_data": "admin_send_user"}],
        ]
    }
    requests.post(API + "sendMessage", json={
        "chat_id": chat_id,
        "text": "📬 منوی ادمین - یک گزینه انتخاب کنید:",
        "reply_markup": keyboard
    })

def send(chat_id, text):
    requests.post(API + "sendMessage", json={"chat_id": chat_id, "text": text})

def answer_callback(callback_id, text):
    requests.post(API + "answerCallbackQuery", json={
        "callback_query_id": callback_id,
        "text": text
    })

@app.route("/")
def home():
    return "VPN Bot is running ✅"
