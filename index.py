import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import psycopg2

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

bot = telebot.TeleBot(BOT_TOKEN)

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Проект", callback_data="project"),
        InlineKeyboardButton("Профиль", callback_data="profile"),
        InlineKeyboardButton("Контакты", callback_data="contacts"),
        InlineKeyboardButton("Квесты", callback_data="quests")
    )
    return markup

# Приветственное сообщение
@bot.message_handler(commands=["start"])
def start(message):
    print("Команда /start получена")  # Отладка
    user_id = message.from_user.id
    username = message.from_user.username.strip().lower() if message.from_user.username else None
    full_name = message.from_user.full_name

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь с таким username
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        user_data = cursor.fetchone()

        if not user_data:
            # Если пользователя нет, создаем новую запись
            cursor.execute("""
                INSERT INTO users (user_id, full_name, username)
                VALUES (%s, %s, %s)
                ON CONFLICT (username) DO NOTHING;
            """, (user_id, full_name, username))
            conn.commit()
            text = f"Профиль создан!\nID: {user_id}\nИмя: {full_name}\nЮзернейм: @{username}"
        else:
            # Если пользователь существует, обновляем данные (если нужно)
            cursor.execute("""
                UPDATE users
                SET full_name = %s
                WHERE username = %s;
            """, (full_name, username))
            conn.commit()
            # welcome текст для существующих пользователей
            text = f"Добро пожаловать обратно!\nID: {user_data[0]}\nИмя: {user_data[1]}\nЮзернейм: @{user_data[2]}"

        conn.close()

        photo_path = "welcome_image.png" # картинка велкам
        with open(photo_path, "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=text,
                reply_markup=main_menu()
            )

    except Exception as e:
        print(f"Ошибка БД: {e}")
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    print(f"Нажата кнопка: {call.data}")  # Отладка
    try:
        if call.data == "quests":
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("НАЧАЛО", callback_data="quest_nachalo"),
                InlineKeyboardButton("Назад", callback_data="back_main")
            )
            if call.message.content_type == "photo":
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(
                    call.message.chat.id,
                    "Доступные квесты:",
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    "Доступные квесты:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )
        
        elif call.data == "quest_nachalo":
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("БРОНИРОВАТЬ", url="https://t.me/@Proektor_straha"),
                InlineKeyboardButton("Назад", callback_data="quests")
            )
            new_photo_path = "nachalo_image.png"
            with open(new_photo_path, "rb") as new_photo:
                bot.edit_message_media(
                    media=InputMediaPhoto(
                        new_photo,
                        caption='Вы заперты в старом доме. Здесь жил маньяк Виктор Крейн...'
                    ),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
        
        elif call.data == "project":
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Назад", callback_data="back_main"))  # Удалены "Трофеи" и "Правила"
            new_photo_path = "project_image.png"
            with open(new_photo_path, "rb") as new_photo:
                bot.edit_message_media(
                    media=InputMediaPhoto(new_photo, caption="Описание проекта..."),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
        
        # Удалены блоки обработки "trophies" и "rules"
        
        elif call.data == "profile":
            user_id = call.from_user.id
            username = call.from_user.username.strip().lower() if call.from_user.username else None
            full_name = call.from_user.full_name
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
            user_data = cursor.fetchone()
            
            if not user_data:
                cursor.execute("""
                    INSERT INTO users (user_id, full_name, username)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (username) DO NOTHING;
                """, (user_id, full_name, username))
                conn.commit()
                text = f"Профиль создан!\nID: {user_id}\nИмя: {full_name}\nЮзернейм: @{username}"
            else:
                text = (
                    f"Ваш профиль:\n"
                    f"ID: {user_data[0]}\n"
                    f"Имя: {user_data[1]}\n"
                    f"Юзернейм: @{user_data[2]}\n"
                    f"Телефон: {user_data[3] or 'Не указан'}\n\n"
                    f"Квестов выполнено: {user_data[4]}\n"
                    f"Трофеев получено: {user_data[5]}\n"
                    f"Общие очки: {user_data[6]}"
                )
            
            conn.close()
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Назад", callback_data="back_main"))
            if call.message.content_type == "photo":
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, text, reply_markup=markup)
            else:
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        
        elif call.data == "contacts":
            text = (
                "Наши контакты:\n"
                "📞 Телефон: +7 (999) 123-45-67\n"
                "📧 Email: info@proektor-straha.ru\n"
                "📍 Адрес: г. Москва, ул. Страшная, д. 13\n"
                "🌐 Сайт: https://proektor-straha.ru"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Назад", callback_data="back_main"))
            if call.message.content_type == "photo":
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, text, reply_markup=markup)
            else:
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        
        elif call.data == "back_main":
            if call.message.content_type == "photo":
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, "Выберите опцию:", reply_markup=main_menu())
            else:
                bot.edit_message_text("Выберите опцию:", call.message.chat.id, call.message.message_id, reply_markup=main_menu())

    except Exception as e:
        print(f"Ошибка в обработке callback: {e}")
        if "there is no text in the message to edit" in str(e):
            bot.send_message(call.message.chat.id, "Не удалось отредактировать сообщение, так как оно не содержит текста.")
# Запуск бота
bot.polling(none_stop=True)
