import logging
from flask import Flask, render_template, jsonify
import telebot
import time
import threading

# --- CONFIG ---
TOKEN = "7829287573:AAG7WTzEiFkFBSLvKtxRhuXGJJoJnI5XzUw"
ADMIN_ID = 5937612986
USER_INFO_FILE = "user_info.txt"
CHANNEL_USERNAME = "@NathanFX_Signal"

# --- TELEGRAM BOT ---
bot = telebot.TeleBot(TOKEN)
logging.basicConfig(level=logging.INFO)

# State for /signal and /channelsignal
waiting_signal_input = {}

# --- UTIL FUNCTIONS ---
def load_user_info():
    try:
        with open(USER_INFO_FILE, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        user_dict = {}
        for l in lines:
            uid, name = l.split(",",1)
            user_dict[int(uid)] = name.strip()
        return user_dict
    except FileNotFoundError:
        return {}

def load_user_ids():
    return list(load_user_info().keys())

def save_user_info(user_id, full_name):
    users = load_user_info()
    if user_id not in users:
        with open(USER_INFO_FILE, "a") as f:
            f.write(f"{user_id},{full_name}\n")

# --- TELEGRAM HANDLERS ---
def not_authorized(chat_id):
    bot.send_message(chat_id, "⛔ You are not authorized to use this command.")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    save_user_info(user_id, full_name)
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton("💎 VIP GROUP SIGNAL", url="https://t.me/nathanaeru"),
        telebot.types.InlineKeyboardButton("⭐ TRUSTED BROKER", url="https://one.exnesstrack.org/a/ntjb1puay7")
        )
    welcome_message = (
        "👋 *Welcome to Nathan FX Trade!*\n\n"
        "This is your time for high-profit signals. 💰\n"
        "You’ll enjoy profit with us — stay alert!\n\n"
        "_We don’t have specific times for trades, once a signal is ready, you’ll receive it instantly._\n\n"
        "*Signal with Setup, You can learn while staying profitable.*"
    )
    bot.send_message(message.chat.id, welcome_message, reply_markup=keyboard, parse_mode="Markdown")

@bot.message_handler(commands=['signal'])
def send_signal(message):
    if message.from_user.id != ADMIN_ID:
        not_authorized(message.chat.id)
        return
    if message.reply_to_message:
        reply_msg = message.reply_to_message
        users = load_user_ids()
        sent = 0
        if reply_msg.photo:
            caption = reply_msg.caption or ""
            for uid in users:
                try:
                    bot.send_photo(chat_id=uid, photo=reply_msg.photo[-1].file_id,
                                   caption=f"📢 Signal Update:\n\n{caption}\n\nForwarded from {CHANNEL_USERNAME}")
                    sent += 1
                except Exception as e:
                    logging.error(f"Error to {uid}: {e}")
        elif reply_msg.text:
            text = f"📢 Signal Update:\n\n{reply_msg.text}\n\nForwarded from {CHANNEL_USERNAME}"
            for uid in users:
                try:
                    bot.send_message(chat_id=uid, text=text)
                    sent += 1
                except Exception as e:
                    logging.error(f"Error to {uid}: {e}")
        else:
            bot.send_message(message.chat.id, "⚠️ Jenis pesan belum didukung.")
        bot.send_message(message.chat.id, f"✅ Sent to {sent} user(s).")
    else:
        waiting_signal_input[message.from_user.id] = 'signal'
        bot.send_message(message.chat.id, "📝 Kirim teks atau foto untuk sinyal ke user.")

@bot.message_handler(func=lambda msg: waiting_signal_input.get(msg.from_user.id)=='signal', content_types=['text','photo'])
def handle_signal_input(message):
    if message.from_user.id != ADMIN_ID: return
    users = load_user_ids(); sent=0
    if message.photo:
        caption = message.caption or ""
        for uid in users:
            try:
                bot.send_photo(chat_id=uid, photo=message.photo[-1].file_id,
                               caption=f"📢 Signal Update:\n\n{caption}\n\nForwarded from {CHANNEL_USERNAME}")
                sent+=1
            except Exception as e:
                logging.error(f"Error to {uid}: {e}")
    else:
        text = message.text
        for uid in users:
            try:
                bot.send_message(chat_id=uid,text=f"📢 Signal Update:\n\n{text}\n\nForwarded from {CHANNEL_USERNAME}")
                sent+=1
            except Exception as e:
                logging.error(f"Error to {uid}: {e}")
    bot.send_message(message.chat.id,f"✅ Sent to {sent} user(s).")
    waiting_signal_input.pop(message.from_user.id,None)

@bot.message_handler(commands=['channelsignal'])
def send_channel_signal(message):
    if message.from_user.id!=ADMIN_ID:
        not_authorized(message.chat.id); return
    if message.reply_to_message:
        r=message.reply_to_message; sent=0
        if r.photo:
            cap=r.caption or ""
            try: bot.send_photo(chat_id=CHANNEL_USERNAME,photo=r.photo[-1].file_id,
                                caption=f"📢 Signal Update:\n\n{cap}\n\nForwarded from {CHANNEL_USERNAME}"); sent=1
            except Exception as e: logging.error(e)
        elif r.text:
            try: bot.send_message(chat_id=CHANNEL_USERNAME,text=f"📢 Signal Update:\n\n{r.text}\n\nForwarded from {CHANNEL_USERNAME}"); sent=1
            except Exception as e: logging.error(e)
        else: bot.send_message(message.chat.id,"⚠️ Tipe pesan tidak didukung.")
        bot.send_message(message.chat.id,f"✅ Sent to channel.")
    else:
        waiting_signal_input[message.from_user.id]='channelsignal'
        bot.send_message(message.chat.id,"📝 Kirim teks atau foto untuk sinyal ke channel.")

@bot.message_handler(func=lambda msg: waiting_signal_input.get(msg.from_user.id)=='channelsignal', content_types=['text','photo'])
def handle_channel_signal_input(message):
    if message.from_user.id!=ADMIN_ID: return
    sent=0
    if message.photo:
        cap=message.caption or ""
        try: bot.send_photo(chat_id=CHANNEL_USERNAME,photo=message.photo[-1].file_id,
                            caption=f"📢 Signal Update:\n\n{cap}\n\nForwarded from {CHANNEL_USERNAME}"); sent=1
        except Exception as e: logging.error(e)
    else:
        try: bot.send_message(chat_id=CHANNEL_USERNAME,text=f"📢 Signal Update:\n\n{message.text}\n\nForwarded from {CHANNEL_USERNAME}"); sent=1
        except Exception as e: logging.error(e)
    bot.send_message(message.chat.id,f"✅ Sent to channel.")
    waiting_signal_input.pop(message.from_user.id,None)

@bot.message_handler(commands=['messageall'])
def send_message_all(message):
    if message.from_user.id!=ADMIN_ID: not_authorized(message.chat.id); return
    parts=message.text.split(maxsplit=1)
    if len(parts)<2: bot.send_message(message.chat.id,"Usage: /messageall msg"); return
    text=parts[1]; users=load_user_ids(); sent=0
    for uid in users:
        try: bot.send_message(chat_id=uid,text=text); sent+=1
        except Exception as e: logging.error(e)
    bot.send_message(message.chat.id,f"✅ Message sent to {sent} user(s).")

@bot.message_handler(commands=['privateusers'])
def send_user(message):
    if message.from_user.id!=ADMIN_ID: not_authorized(message.chat.id); return
    p=message.text.split(maxsplit=2)
    if len(p)<3: bot.send_message(message.chat.id,"Usage: /privateusers id msg"); return
    tid=int(p[1]); msg=p[2]
    try: bot.send_message(chat_id=tid,text=msg); bot.send_message(message.chat.id,f"✅ Sent to {tid}")
    except Exception as e: logging.error(e); bot.send_message(message.chat.id,"❌ Gagal kirim.")

@bot.message_handler(commands=['users'])
def show_total(message):
    info=load_user_info()
    if not info: bot.send_message(message.chat.id,"ℹ️ No users"); return
    lst="\n".join([f"👤 {uid} - {name}" for uid,name in info.items()])
    bot.send_message(message.chat.id,f"📋 Total Users:\n\n{lst}")

@bot.message_handler(commands=['cancel'])
def cancel_operation(message):
    if message.from_user.id!=ADMIN_ID: not_authorized(message.chat.id); return
    if waiting_signal_input.pop(message.from_user.id,None): bot.send_message(message.chat.id,"✅ Canceled.")
    else: bot.send_message(message.chat.id,"ℹ️ No pending.")

# --- FLASK APP ---
app = Flask(__name__)
start_time = time.time()

@app.route('/')
def index():
    users = load_user_info()
    total = len(users)
    # Calculate uptime
    elapsed = int(time.time() - start_time)
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    uptime = f"{hours}h {minutes}m {seconds}s"
    # Pass data to template
    return render_template('index.html',
                       total=total,
                       users=users,
                       uptime=uptime,
                       bot_username=bot.get_me().username,
                       channel_username=CHANNEL_USERNAME.strip('@'),
                       developer_username='nathanaeru')
@app.route('/status')
def status(): return jsonify({'status':'Online'})

def run_flask(): app.run(host='0.0.0.0',port=8080)

if __name__=='__main__':
    threading.Thread(target=run_flask,daemon=True).start()
    bot.polling()
