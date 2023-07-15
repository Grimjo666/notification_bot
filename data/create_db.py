import sqlite3


def create_database():
    # Установка соединения с базой данных
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS models (
                        model_email TEXT PRIMARY KEY,
                        model_nickname TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_model_access (
                        access_id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        model_email INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users (user_id),
                        FOREIGN KEY (model_email) REFERENCES models (model_email)
                    )''')

    # Фиксация изменений и закрытие соединения
    conn.commit()
    conn.close()
