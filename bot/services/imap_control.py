import imaplib
import email
from bot import config


def subject_filter(subject: str, message_notifications: int, purchase_notifications: int, other_notifications: int) -> bool:
    if message_notifications == 1 and 'message' in subject:
        return False
    elif purchase_notifications == 1 and any(word in subject for word in ('purchase', '$', 'renewed')):
        return False
    elif other_notifications == 1:
        return False
    else:
        return True


def is_valid_imap_credentials(user_email, password):
    try:
        # Подключаемся к IMAP-серверу с предоставленными данными
        imap = imaplib.IMAP4_SSL('imap.example.com')
        imap.login(user_email, password)
        imap.logout()
        return True
    except imaplib.IMAP4.error as e:
        # Обрабатываем ошибку в случае неверных данных
        print(f"Ошибка: {e}")
        return False


def get_new_message(username, mail_pass) -> list:
    # Получаем логин и пароль от почты для парсинг по imap и возвращаем список с данными о сообщениях

    message_list = []
    imap_server = config.IMAP_SERVER

    # Подключение к серверу IMAP
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, mail_pass)

    for elem in config.EMAIL_FOLDERS:
        # Выбор почтового ящика
        imap.select(elem)

        # Поиск непрочитанных сообщений
        typ, msg_nums = imap.search(None, config.IMAP_CRITERIA)

        # Обработка каждого найденного сообщения
        for num in msg_nums[0].split():
            # Получение сообщения по его номеру
            typ, msg_data = imap.fetch(num, '(RFC822)')
            raw_email = msg_data[0][1]

            # Парсинг сообщения
            email_message = email.message_from_bytes(raw_email)

            sender = email_message['From']

            if 'fansly' not in sender.lower():
                continue

            # Извлечение заголовка
            subject = email_message['Subject']

            if 'your code is' in subject.lower():
                continue

            recipient = email_message['To']
            text = ''

            # Извлечение текста сообщения
            if email_message.is_multipart():
                # Если сообщение состоит из нескольких частей (multipart), ищем текстовую часть
                for part in email_message.get_payload():
                    if part.get_content_type() == 'text/plain':
                        text = part.get_payload(decode=True).decode(part.get_content_charset())
                        break
            else:
                # Если сообщение состоит из одной части, это может быть просто текстовое сообщение
                text = email_message.get_payload(decode=True).decode(email_message.get_content_charset())

            message_list.append((subject, recipient, text))

            # Отметка сообщения как прочитанного
            imap.store(num, '+FLAGS', '\\Seen')

        # Завершение работы с сервером IMAP
    imap.logout()

    return message_list


