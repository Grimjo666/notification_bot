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


def add_email(email, name=None):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM emails WHERE email = ?', (email,))
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute('INSERT INTO emails (email, nickname) VALUES (?, ?)',
                       (email, name))
    else:
        cursor.execute('UPDATE emails SET nickname = ? WHERE email = ?',
                       (name, email))

    conn.commit()
    conn.close()


def get_email_name(email):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT nickname FROM emails WHERE email = ?', (email,))
    name = cursor.fetchone()

    conn.close()

    if name is not None and len(name) > 0:
        return name
    else:
        return False


def del_email(email):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM emails WHERE email = ?', (email,))

    conn.commit()
    conn.close()


def set_user_email_notification(user_id, email):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    if not check_user_email_notification(user_id, email):
        cursor.execute('INSERT INTO user_email_notifications (user_id, email) VALUES (?, ?)',
                       (user_id, email))

    conn.commit()
    conn.close()


def check_user_email_notification(user_id, email):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM user_email_notifications WHERE user_id = ? AND email = ?',
                   (user_id, email))
    count = cursor.fetchone()[0]

    conn.close()

    return count > 0


def get_all_user_email_notification(user_id):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT email FROM user_email_notifications WHERE user_id = ?',
                   (user_id,))

    user_notifications = cursor.fetchall()

    conn.close()

    return user_notifications


def get_user_email_notification_id(user_id, email):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT notification_id FROM user_email_notifications WHERE user_id = ? AND email = ?',
                   (user_id, email))
    access_id = cursor.fetchone()[0]

    return access_id


def del_user_email_notification(notification_id):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM user_email_notifications WHERE notification_id = ?', (notification_id,))

    conn.commit()
    conn.close()


def del_all_user_email_notifications(user_id):
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM user_email_notifications WHERE user_id = ?', (user_id,))

    conn.commit()
    conn.close()


def get_all_emails():
    conn = sqlite3.connect('data/bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM emails')
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

