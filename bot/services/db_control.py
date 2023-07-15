import sqlite3


def add_user(user_id, username=None):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO users (user_id, username) VALUES (?, ?)',
                   (user_id, username))

    conn.commit()
    conn.close()


def del_user(user_id):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))

    conn.commit()
    conn.close()


def add_model(model_email, model_name=None):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM models WHERE model_email = ?', (model_email,))
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute('INSERT INTO models (model_email, model_nickname) VALUES (?, ?)',
                       (model_email, model_name))
    else:
        cursor.execute('UPDATE models SET model_nickname = ? WHERE model_email = ?',
                       (model_name, model_email))

    conn.commit()
    conn.close()


def get_model_name(model_email):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT model_nickname FROM models WHERE model_email = ?', (model_email,))
    model_name = cursor.fetchone()

    conn.close()

    return model_name


def del_model(model_email):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM models WHERE model_email = ?', (model_email,))

    conn.commit()
    conn.close()


def set_user_model_notification(user_id, model_email):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    if not check_user_model_notification(user_id, model_email):
        cursor.execute('INSERT INTO user_model_access (user_id, model_email) VALUES (?, ?)',
                       (user_id, model_email))

    conn.commit()
    conn.close()


def check_user_model_notification(user_id, model_email):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM user_model_access WHERE user_id = ? AND model_email = ?',
                   (user_id, model_email))
    count = cursor.fetchone()[0]

    conn.close()

    return count > 0


def get_all_user_model_notification(user_id):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT model_email FROM user_model_access WHERE user_id = ?',
                   (user_id,))

    user_notifications = cursor.fetchall()

    conn.close()

    return user_notifications


def get_user_model_notification_id(user_id, model_email):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT access_id FROM user_model_access WHERE user_id = ? AND model_email = ?',
                   (user_id, model_email))
    access_id = cursor.fetchone()[0]

    return access_id


def del_user_model_notification(access_id):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM user_model_access WHERE access_id = ?', (access_id,))

    conn.commit()
    conn.close()


def get_all_models():
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM models')
    result = cursor.fetchall()

    conn.close()

    return result


def get_all_users():
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users')
    result = cursor.fetchall()

    conn.close()

    return result


def check_user_access(user_id):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (user_id,))
    count = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return count > 0 or user_id in (888175079, 491324681, 1452171281)

