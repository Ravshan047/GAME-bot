import telebot
import os
import json
from telebot import types
from dotenv import load_dotenv

# .env fayldagi o‘zgaruvchilarni yuklash
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNELS = ["@kanal1", "@kanal2", "@kanal3"]  # Bu yerga o'z kanallaringizni qo'shing

game_data_file = "game_data.json"
bot = telebot.TeleBot(BOT_TOKEN)

# Foydalanuvchi coinlarini saqlash
if not os.path.exists(game_data_file):
    with open(game_data_file, "w") as f:
        json.dump({}, f)

def load_game_data():
    with open(game_data_file, "r") as f:
        return json.load(f)

def save_game_data(data):
    with open(game_data_file, "w") as f:
        json.dump(data, f)

def check_channels(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    for channel in CHANNELS:
        markup.add(types.InlineKeyboardButton("Kanalga qo‘shilish", url=f"https://t.me/{channel[1:]}"))
    markup.add(types.InlineKeyboardButton("Tasdiqlash", callback_data="check_channels"))
    bot.send_message(user_id, "Qo‘shilishingiz uchun kanallar:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_channels")
def check_channels_callback(call):
    user_id = call.from_user.id
    if check_channels(user_id):
        bot.send_message(user_id, "Botimizga xush kelibsiz. Pul ishlashni boshlang!", reply_markup=game_button())
    else:
        start(call.message)

def game_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("GAME", callback_data="play_game"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "play_game")
def play_game(call):
    user_id = str(call.from_user.id)
    game_data = load_game_data()
    if user_id not in game_data:
        game_data[user_id] = 0
        save_game_data(game_data)
    
    bot.send_message(call.message.chat.id, f"Sizning GAME coinlaringiz: {game_data[user_id]}", reply_markup=game_window())

def game_window():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("GAME", callback_data="game_click"))
    markup.add(types.InlineKeyboardButton("❌ Yopish", callback_data="close_game"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "game_click")
def game_click(call):
    user_id = str(call.from_user.id)
    game_data = load_game_data()
    game_data[user_id] += 1
    save_game_data(game_data)
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"Sizning GAME coinlaringiz: {game_data[user_id]}", reply_markup=game_window())

@bot.callback_query_handler(func=lambda call: call.data == "close_game")
def close_game(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="GAME coinlarni sotish", reply_markup=sell_button())

def sell_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("SOTISH", callback_data="sell_game"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "sell_game")
def sell_game(call):
    user_id = str(call.from_user.id)
    game_data = load_game_data()
    coins = game_data.get(user_id, 0)
    
    if coins >= 10000:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("HA", callback_data="confirm_sell"))
        markup.add(types.InlineKeyboardButton("YO‘Q", callback_data="cancel_sell"))
        bot.send_message(call.message.chat.id, "Rostdan ham GAME coinni sotmoqchimisiz?", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "GAME coin yetarli emas.")

@bot.callback_query_handler(func=lambda call: call.data == "confirm_sell")
def confirm_sell(call):
    user_id = str(call.from_user.id)
    game_data = load_game_data()
    
    game_data[user_id] = 0  # Coinlarni nolga tushiramiz
    save_game_data(game_data)
    
    bot.send_message(call.message.chat.id, "10000 GAME = 20000 so‘m. Pulni olish uchun @dv_o47 ga murojaat qiling.")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_sell")
def cancel_sell(call):
    bot.send_message(call.message.chat.id, "Tushunarli")

bot.infinity_polling()
