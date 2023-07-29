import sqlite3
import bcrypt
from datetime import datetime, timedelta


class DBErrors(Exception):
    def __init__(self, message="Ошибка при работе с базой данных"):
        self.message = message
        super().__init__(self.message)


class BotDataBase:

    def __init__(self):
        self.conn = sqlite3.connect('data/bot_data.db')
        self.cursor = self.conn.cursor()

    @staticmethod
    def hash_password(password) -> str:
        # Генерируем соль (случайное значение)
        salt = bcrypt.gensalt()

        # Хешируем пароль с использованием соли
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Преобразуем хеш в строку для сохранения в базу данных
        return hashed_password.decode('utf-8')

    @staticmethod
    def check_password(password, hashed_password) -> bool:
        # Проверяем, соответствует ли хеш заданному паролю
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    # Удаляем запись из переданной таблицы по user_id
    def del_from_table_by_user_id(self, user_id, table_name):
        self.cursor.execute(f'''DELETE FROM {table_name} WHERE user_id = ?''', (user_id,))
        self.conn.commit()

    # Добавляем запрос на регистрацию аккаунта в БД
    def add_buy_request(self, user_id, user_name, email_login, email_password, subscription_type):
        self.cursor.execute('''INSERT OR REPLACE INTO buy_requests (
                                user_id,
                                user_name,
                                email_login,
                                email_password,
                                subscription_type
                                ) VALUES (?, ?, ?, ?, ?)''',
                            (user_id, user_name, email_login, email_password, subscription_type))
        self.conn.commit()

    # Добавляем аккаунт в БД
    def add_bot_account(self, user_id, email_login, email_password, subscription_type, subscription_status,
                        subscription_expiration_date, number_of_available_users=100, number_of_available_emails=500):
        self.cursor.execute('''SELECT COUNT(*) FROM bot_accounts WHERE user_id = ?''', (user_id,))
        exists_account = self.cursor.fetchone()[0]

        if exists_account == 0:
            self.cursor.execute('''INSERT INTO bot_accounts (user_id,
                                                            email_login,
                                                            email_password,
                                                            subscription_type,
                                                            subscription_status,
                                                            subscription_expiration_date,
                                                            number_of_available_users,
                                                            number_of_available_emails) 
                                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                (user_id, email_login, email_password, subscription_type, subscription_status,
                                 subscription_expiration_date, number_of_available_users,
                                 number_of_available_emails))
            self.conn.commit()
        else:
            raise DBErrors('Аккаунт уже существует')

    # Обновляем аккаунт пользователя
    def update_bot_account(self, user_id, subscription_type, subscription_status,
                           subscription_expiration_date, number_of_available_users, number_of_available_emails):
        self.cursor.execute('''UPDATE bot_accounts SET email_login = ?,
                                                    subscription_type = ?,
                                                    subscription_expiration_date = ?,
                                                    number_of_available_users = ?,
                                                    number_of_available_emails = ?
                                                    WHERE user_id = ?''',
                            (subscription_type, subscription_status, subscription_expiration_date,
                             number_of_available_users, number_of_available_emails, user_id))
        self.conn.commit()

    # Добавляем доступ к аккаунту для нового телеграм-пользователя
    def add_authorized_user(self, user_id, user_name, email_login, message_notifications=1,
                            purchase_notifications=1, other_notifications=1):
        # Получаем количество доступных пользователей и добавленных пользователей к аккаунту
        self.cursor.execute('''SELECT number_of_available_users, COUNT(*) FROM bot_accounts 
                                       LEFT JOIN authorized_users USING(email_login)
                                       WHERE email_login = ? GROUP BY email_login''', (email_login,))
        result = self.cursor.fetchone()

        if result is None:
            raise DBErrors('Аккаунт не найден')

        count_available_accounts, count_authorized_users = result

        # Если лимит пользователей не превышен, добавляем нового
        if count_available_accounts > count_authorized_users:
            self.cursor.execute('''INSERT INTO authorized_users (user_id,
                                                                user_name,
                                                                message_notifications,
                                                                purchase_notifications,
                                                                other_notifications,
                                                                email_login)
                                                                VALUES (?, ?, ?, ?, ?, ?)''',
                                (user_id, user_name, message_notifications,
                                 purchase_notifications, other_notifications, email_login))
            self.conn.commit()
        else:
            raise DBErrors('Вы не можете дать доступ новому пользователю\n'
                           f'Доступных аккаунтов телеграм:{count_available_accounts}\n'
                           f'Действующих аккаунтов телеграм:{count_authorized_users}')

    # Переключаем состояние фильтров уведомлений пользователя, па умолчанию все включены(switch)
    def switch_filters_notifications(self, user_id, message_notifications=1, purchase_notifications=1,
                                     other_notifications=1, switch=True):
        if not switch:
            message_notifications, purchase_notifications, other_notifications = 0, 0, 0

        self.cursor.execute('''UPDATE authorized_users SET message_notifications = ?,
                                                           purchase_notifications = ?,
                                                           other_notifications = ?
                                                           WHERE user_id = ?''',
                            (message_notifications, purchase_notifications, other_notifications, user_id))
        self.conn.commit()

    # Добавляем email-уведомление в аккаунт
    def add_account_notification(self, message_email, notification_name, email_login):
        # Получаем количество доступных email-адресов в аккаунте
        self.cursor.execute('''SELECT number_of_available_emails, COUNT(*) FROM bot_accounts 
                               LEFT JOIN account_notifications USING(email_login)
                               WHERE email_login = ? GROUP BY email_login''', (email_login,))
        result = self.cursor.fetchone()

        if result is None:
            raise DBErrors('Аккаунт не найден')

        count_available_emails, count_account_notifications = result

        # Если количество доступных email-адресов превышает количество добавленных уведомлений, добавляем новую запись
        if count_available_emails > count_account_notifications:
            self.cursor.execute('''INSERT INTO account_notifications (message_email, notification_name, email_login)
                                    VALUES (?, ?, ?)''', (message_email, notification_name, email_login))
            self.conn.commit()
        else:
            raise DBErrors('Вы не можете добавить новое уведомление\n'
                           f'Доступных email-адресов:{count_available_emails}\n'
                           f'Добавленных уведомлений:{count_account_notifications}')

    # Проверяем, есть ли уведомление в базе данных
    def check_notification_exist(self, notification_id):
        self.cursor.execute('''SELECT COUNT(*) FROM account_notifications WHERE notification_id = ?''',
                            (notification_id,))
        notification_exist = self.cursor.fetchone()[0]
        return notification_exist != 0

    # Удаляем уведомление с аккаунта
    def del_account_notification(self, notification_id, notification_name):
        if self.check_notification_exist(notification_id):
            self.cursor.execute('''DELETE FROM account_notifications WHERE notification_id = ?''',
                                (notification_id,))
            self.conn.commit()
        else:
            raise DBErrors(f'Невозможно удалить уведомление {notification_name}, его не существует')

    # Меняем имя уведомления
    def edit_account_notification_name(self, notification_id, notification_name):
        if self.check_notification_exist(notification_id):
            self.cursor.execute('''UPDATE account_notifications SET notification_name = ? WHERE notification_id = ?''',
                                (notification_name, notification_id))
            self.conn.commit()

        else:
            raise DBErrors('Не возможно изменить имя уведомления, уведомления не существует ')

    # Проверяем, есть ли пользователь в базе данных
    def check_user_exist(self, user_id):
        self.cursor.execute('''SELECT COUNT(*) FROM authorized_users WHERE user_id = ?''', (user_id,))
        user_exist = self.cursor.fetchone()[0]

        return user_exist > 0

    def close(self):
        self.conn.close()

    # Получаем текущую дату
    @staticmethod
    def get_current_datetime() -> datetime:
        return datetime.now()

    # Прибавляем к переданной переданное количество дней, по умолчанию 1
    @staticmethod
    def add_days(date: datetime, count_days=1) -> datetime:
        return date + timedelta(days=count_days)

    # Проверяем является ли передаваемая дата больше текущий даты
    def check_expiration_date(self, date: datetime) -> bool:
        current_date = self.get_current_datetime()
        return date > current_date

    # Поучаем текущую дату и возвращаем дату истечения бесплатной подписки в формате str
    def get_free_subscription_expiration_date(self) -> str:
        date = self.get_current_datetime()
        return self.add_days(date, 2).strftime('%Y-%m-%d %H:%M:%S')
