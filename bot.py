import telebot
from datetime import datetime, timedelta

TOKEN = '7465745734:AAHnr3_5gYZsC7m2L_92BZW72rA9jHBHago'
GROUP_ID = -1001855011523
OWNER = '@Владелец'  # Укажите владельца группы
ADMIN_USERNAMES = ['@TheFoZzYq']
ADMIN_IDS = [1653222949]

bot = telebot.TeleBot(TOKEN)
ban_list = []
mute_list = []

# Проверка администратора
def is_admin(user_id):
    return user_id in ADMIN_IDS

# Преобразование времени бана
def parse_ban_time(ban_time_str):
    time_units = {
        'год': 'days',
        'час': 'hours',
        'день': 'days',
        'минута': 'minutes',
        'секунда': 'seconds'
    }
    for unit, unit_en in time_units.items():
        if unit in ban_time_str:
            amount = int(ban_time_str.replace(unit, '').strip())
            return timedelta(**{unit_en: amount})
    return None

# Команда /help
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = """
Команды управления:
- /ban время причина: Забанить пользователя на определённый период. Например, /ban 1год Спам.
- /ban_forever причина: Забанить пользователя навсегда. Например, /ban_forever Спам.
- /unban: Разбанить пользователя.
- /mute время причина: Замутить пользователя на определённый период. Например, /mute 1час Нарушение правил.
- /unmute: Размутить пользователя.
- /banlist: Показать список забаненных пользователей.
- /mutelist: Показать список замученных пользователей.

Русские команды:
- бан: Забанить пользователя навсегда. Работает только при ответе на сообщение пользователя.
- мут: Замутить пользователя навсегда. Работает только при ответе на сообщение пользователя.
- разбан: Разбанить пользователя. Работает только при ответе на сообщение пользователя.
- размут: Размутить пользователя. Работает только при ответе на сообщение пользователя.
- админы: Показать список администраторов.
    """
    bot.reply_to(message, help_text)

# Команда "админы"
@bot.message_handler(func=lambda message: message.text.lower() == 'админы')
def show_admins(message):
    admin_list = '\n'.join(ADMIN_USERNAMES)
    response = f"Владелец:\n{OWNER}\n\nПупсики на админке:\n{admin_list}"
    bot.reply_to(message, response)

# Команда бана
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Вы не администратор.")
        return

    try:
        parts = message.text.split()
        ban_duration = parse_ban_time(parts[1])
        reason = ' '.join(parts[2:])
        if ban_duration:
            until_date = datetime.now() + ban_duration
            bot.ban_chat_member(GROUP_ID, message.reply_to_message.from_user.id, until_date=until_date.timestamp())
            ban_list.append((message.reply_to_message.from_user.username, until_date, reason))
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} забанен до {until_date}.\nПричина: {reason}")
        else:
            bot.reply_to(message, "Некорректное время бана.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

# Команда бана навсегда
@bot.message_handler(commands=['ban_forever'])
def ban_forever(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Вы не администратор.")
        return

    try:
        reason = ' '.join(message.text.split()[1:])
        bot.ban_chat_member(GROUP_ID, message.reply_to_message.from_user.id)
        ban_list.append((message.reply_to_message.from_user.username, 'Навсегда', reason))
        bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} забанен навсегда.\nПричина: {reason}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

# Команда разбана
@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Вы не администратор.")
        return

    try:
        bot.unban_chat_member(GROUP_ID, message.reply_to_message.from_user.id)
        global ban_list
        ban_list = [entry for entry in ban_list if entry[0] != message.reply_to_message.from_user.username]
        bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} разбанен.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

# Команда мута
@bot.message_handler(commands=['mute'])
def mute_user(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Вы не администратор.")
        return

    try:
        parts = message.text.split()
        mute_duration = parse_ban_time(parts[1])
        reason = ' '.join(parts[2:])
        
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            username = message.reply_to_message.from_user.username
        else:
            username = parts[2].lstrip('@')
            user_id = bot.get_chat_member(GROUP_ID, username).user.id
        
        if mute_duration:
            until_date = datetime.now() + mute_duration
            bot.restrict_chat_member(GROUP_ID, user_id, can_send_messages=False, until_date=until_date.timestamp())
            mute_list.append((username, until_date, reason))
            bot.reply_to(message, f"Пользователь {username} замучен до {until_date}.\nПричина: {reason}")
        else:
            bot.reply_to(message, "Некорректное время мута.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

# Команда размут
@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Вы не администратор.")
        return

    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            username = message.reply_to_message.from_user.username
        else:
            username = message.text.split()[1]
            user_id = bot.get_chat_member(GROUP_ID, username).user.id
        
        bot.restrict_chat_member(GROUP_ID, user_id, can_send_messages=True)
        global mute_list
        mute_list = [entry for entry in mute_list if entry[0] != username]
        bot.reply_to(message, f"Пользователь {username} размучен.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

# Команда /banlist
@bot.message_handler(commands=['banlist'])
def show_banlist(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Вы не администратор.")
        return

    if not ban_list:
        bot.reply_to(message, "Бан-лист пуст.")
    else:
        response = "Бан-лист:\n"
        for i, (username, until_date, reason) in enumerate(ban_list, 1):
            response += f"{i}. {username}\nСрок бана: {until_date}\nПричина бана: {reason}\n\n"
        bot.reply_to(message, response)

# Команда /mutelist
@bot.message_handler(commands=['mutelist'])
def show_mutelist(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Вы не администратор.")
        return

    if not mute_list:
        bot.reply_to(message, "Мут-лист пуст.")
    else:
        response = "Мут-лист:\n"
        for i, (username, until_date, reason) in enumerate(mute_list, 1):
            response += f"{i}. {username}\nСрок мута: {until_date}\nПричина мута: {reason}\n\n"
        bot.reply_to(message, response)

# Русская команда бан
@bot.message_handler(func=lambda message: message.text.lower().startswith('бан') and message.reply_to_message is not None)
def ban_forever_ru(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Вы не администратор.")
        return

    try:
        parts = message.text.split('\n', 1)
        reason = parts[1] if len(parts) > 1 else 'Без указания причины'
        bot.ban_chat_member(GROUP_ID, message.reply_to_message.from_user.id)
        ban_list.append((message.reply_to_message.from_user.username, 'Навсегда', reason))
        bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} забанен навсегда.\nПричина: {reason}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

# Русская команда мут
@bot.message_handler(func=lambda message: message.text.lower().startswith('мут') and message.reply_to_message is not None)
def mute_forever_ru(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Вы не администратор.")
        return

    try:
        parts = message.text.split('\n', 1)
        reason = parts[1] if len(parts) > 1 else 'Без указания причины'
        bot.restrict_chat_member(GROUP_ID, message.reply_to_message.from_user.id, can_send_messages=False)
        mute_list.append((message.reply_to_message.from_user.username, 'Навсегда', reason))
        bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} замучен навсегда.\nПричина: {reason}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

# Русская команда разбан
@bot.message_handler(func=lambda message: message.text.lower() == 'разбан' and message.reply_to_message is not None)
def unban_ru(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Вы не администратор.")
        return

    try:
        bot.unban_chat_member(GROUP_ID, message.reply_to_message.from_user.id)
        global ban_list
        ban_list = [entry for entry in ban_list if entry[0] != message.reply_to_message.from_user.username]
        bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} разбанен.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

# Русская команда размут
@bot.message_handler(func=lambda message: message.text.lower() == 'размут' and message.reply_to_message is not None)
def unmute_ru(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Вы не администратор.")
        return

    try:
        bot.restrict_chat_member(GROUP_ID, message.reply_to_message.from_user.id, can_send_messages=True)
        global mute_list
        mute_list = [entry for entry in mute_list if entry[0] != message.reply_to_message.from_user.username]
        bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} размучен.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

# Запуск бота
bot.polling(none_stop=True)