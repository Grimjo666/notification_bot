import sqlite3


def create_database():
    # Установка соединения с базой данных
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS emails (
                        email TEXT PRIMARY KEY,
                        nickname TEXT
                    )''')

    # Фиксация изменений и закрытие соединения
    conn.commit()
    conn.close()


def create_table_notifications():
    # Установка соединения с базой данных
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_email_notifications (
                         notification_id INTEGER PRIMARY KEY,
                         user_id INTEGER,
                         email INTEGER,
                         FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                         FOREIGN KEY (email) REFERENCES emails (email) ON DELETE CASCADE
                     )''')

    conn.commit()
    conn.close()
