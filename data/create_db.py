import sqlite3


def create_database():
    # Установка соединения с базой данных
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    # таблица для записи запросов на доступ к боту
    cursor.execute('''CREATE TABLE IF NOT EXISTS buy_requests (
                        user_id INTEGER PRIMARY KEY,
                        user_name TEXT,
                        email_login TEXT,
                        email_password BLOB,
                        subscription_type TEXT,
                        payment_photo TEXT,
                        payment_type TEXT
                    )''')

    # основная таблица с данными об бот-аккаунтах пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS bot_accounts (
                        user_id INTEGER PRIMARY KEY,
                        email_login TEXT,
                        email_password BLOB,
                        subscription_type TEXT,
                        subscription_status TEXT,
                        subscription_expiration_date TEXT,
                        number_of_available_users INTEGER,
                        number_of_available_emails INTEGER,
                        FOREIGN KEY (user_id) REFERENCES buy_requests (user_id)
                    )''')

    # таблица для доступа других пользователей к зарегистрированному аккаунту
    cursor.execute('''CREATE TABLE IF NOT EXISTS authorized_users (
                        user_id INTEGER PRIMARY KEY,
                        user_name TEXT,
                        message_notifications INTEGER,
                        purchase_notifications INTEGER,
                        other_notifications INTEGER,
                        is_chat INTEGER,
                        email_login TEXT,
                        FOREIGN KEY (email_login) REFERENCES bot_accounts (email_login) ON DELETE CASCADE
                    )''')

    # таблица для управления уведомлениями аккаунта
    cursor.execute('''CREATE TABLE IF NOT EXISTS account_notifications (
                        notification_id INTEGER PRIMARY KEY,
                        email_recipient TEXT,
                        notification_name TEXT,
                        email_login TEXT,
                        FOREIGN KEY (email_login) REFERENCES bot_accounts (email_login) ON DELETE CASCADE
                    )''')

    # таблица для управлением уведомлений пользователя
    cursor.execute('''CREATE TABLE IF NOT EXISTS users_notifications (
                        notification_id INTEGER,
                        user_id INTEGER,
                        is_filtered INTEGER,
                        FOREIGN KEY (user_id) REFERENCES authorized_users (user_id) ON DELETE CASCADE,
                        FOREIGN KEY (notification_id) REFERENCES account_notifications (notification_id) ON DELETE CASCADE
                    )''')

    # таблица админ-доступа к боту
    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                        admin_id INTEGER PRIMARY KEY,
                        admin_name TEXT
                    )''')

    # Фиксация изменений и закрытие соединения
    conn.commit()
    conn.close()


# def hash_password(password):
#     # Генерируем соль (случайное значение)
#     salt = bcrypt.gensalt()
#
#     # Хешируем пароль с использованием соли
#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
#
#     # Преобразуем хеш в строку для сохранения в базу данных
#     return hashed_password.decode('utf-8')
#
#
# def check_password(password, hashed_password):
#     # Проверяем, соответствует ли хеш заданному паролю
#     return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
#
#
# # Пример использования
# password = input()
# hashed_password = hash_password(password)
#
# # Проверяем пароль
# if check_password('1234', hashed_password):
#     print(type(hashed_password))
# else:
#     print("Пароль неверный.")
