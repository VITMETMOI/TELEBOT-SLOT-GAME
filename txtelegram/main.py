import telebot
from telebot import types
import sqlite3
import time
TOKEN = '6819953146:AAHtvF9UeMT6qP45H-FmA8XnHDEGTTwurAg'
bot = telebot.TeleBot(TOKEN)
def menu(message):
    items = ['👤 Tài khoản','🎮 Game']
    markup = types.ReplyKeyboardMarkup(row_width=1)
    buttons = [types.KeyboardButton(item) for item in items]
    markup.add(*buttons)
    bot.send_message(message.chat.id, f"🎉 Chào {message.from_user.first_name} {message.from_user.last_name}, tôi có thể giúp gì cho bạn ?",reply_markup=markup)
def game(message):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("🎲 Tài xỉu", callback_data='button_dice')
    markup.row(item1)
    bot.send_message(message.chat.id, "🎮 Lựa chọn game để chơi 👇👇👇", reply_markup=markup)
def get_user_data(user_id):
    conn = sqlite3.connect('user_balance.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE id_telegram = ?''', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data
def update_balance(user_id, amount):
    conn = sqlite3.connect('user_balance.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT balance FROM users WHERE id_telegram = ?''', (user_id,))
    current_balance = cursor.fetchone()[0]
    new_balance = current_balance + amount
    if new_balance < 0:
        new_balance = 0
    cursor.execute('''UPDATE users SET balance = ? WHERE id_telegram = ?''', (new_balance, user_id))
    conn.commit()
    conn.close()
@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('user_balance.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT OR IGNORE INTO users (id_telegram) VALUES (?)''', (message.from_user.id,))
    conn.commit()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('🎊 ALL READY 🎊', callback_data='button_ready'))
    bot.send_message(message.chat.id,"🎮 Chiến game nào !", reply_markup=markup)
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'button_ready':
        menu(call.message)
    elif call.data == 'button_dice':
        bot.send_message(call.message.chat.id,
                        '🎲 XÚC XẮC TELEGRAM 🎲\n'
                        '👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.\n'
                        '👉 Xúc xắc được quay random bởi Telegram nên hoàn toàn xanh chín.\n'
                        '❗️❗️❗️ Lưu ý: Các biểu tượng Emoji của Telegram click vào có thể tương tác được tránh bị nhầm lẫn các đối tượng giả mạo bằng ảnh gif ❗️❗️❗️'
                        '🔖 Thể lệ:\n'
                        '👍 Kết quả được tính bằng mặt Xúc Xắc Telegram trả về sau khi người chơi đặt cược:\n'
                        'XXT  ➤   x1.95  ➤ Xúc Xắc: > 11\n'
                        'XXX  ➤   x1.95  ➤ Xúc Xắc: < 10\n'
                        '🎮 Cách chơi:\n'
                        '👉 Chat tại đây nội dung như sau:\n'
                        ' "Nội dung" dấu cách "Số tiền cược(VD: T 10000)')


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.split()
    user_data = get_user_data(message.from_user.id)
    if  message.text == '👤 Tài khoản':
        user_data = get_user_data(message.from_user.id)
        if user_data:
            user_info = f"👤 ID: {user_data[0]}\n💰 Số dư: {user_data[1]} TeC\n🎲 Level: {user_data[2]}"
            bot.send_message(message.chat.id, user_info)
        else:
            bot.send_message(message.chat.id, "Không tìm thấy thông tin của người dùng.")
    elif message.text == '🎮 Game':
        game(message)
    elif len(text) == 2 and text[0].upper() in ['T', 'X'] and text[1].isnumeric() and int(text[1]) >= 1000:
        game_dice_play(message)
    elif message.text == 'videvgame': 
        update_balance(message.chat.id, int(10000))
        new_balance = user_data[1] + int(10000)
        bot.send_message(message.chat.id, f'Nạp thành công , số dư của bạn là {new_balance} TeC')
    else:
        bot.send_message(message.chat.id, '❗Nói cái mọe gì vậy ???')
def game_dice_play(message):
    user_data = get_user_data(message.from_user.id)
    text = message.text.split()
    if user_data[1] < int(text[1]):
        bot.reply_to(message, "❌ Nạp thêm đi mày 🎲")
        return
    dice1 = bot.send_dice(message.chat.id, emoji="🎲")
    time.sleep(1)
    dice2 = bot.send_dice(message.chat.id, emoji="🎲")
    time.sleep(1)
    dice3 = bot.send_dice(message.chat.id, emoji="🎲")
    if (text[0].upper() == 'T' and (dice1.dice.value + dice2.dice.value + dice3.dice.value > 10)) or (text[0].upper() == 'X' and (dice1.dice.value + dice2.dice.value + dice3.dice.value < 11)):
        update_balance(message.from_user.id, + int(int(text[1]) * 0.9))
        new_balance = user_data[1] + int(int(text[1]) * 0.9)

        bot.send_message(message.chat.id, 
                        f'♻ Time ID {message.date}\n'
                        f'♻ Kết quả 🎲 : {dice1.dice.value} {dice2.dice.value} {dice3.dice.value}\n'
                        f'♻ Ghi chú : trả thưởng thành công\n'
                        f'💰 Số dư : {new_balance} TeC')
    else:
        update_balance(message.from_user.id, - int(text[1]))
        new_balance = user_data[1] - int(text[1])
        bot.send_message(message.chat.id, 
                        f'💢 Time ID {message.date}\n'
                        f'💢 Kết quả 🎲 : {dice1.dice.value} {dice2.dice.value} {dice3.dice.value}\n'
                        f'💢 Ghi chú: trả thưởng không thành công\n'
                        f'💰 Số dư : {new_balance} TeC')
bot.polling()
