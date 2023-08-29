import imaplib
import email
from bot import config
import base64
from email.header import decode_header


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
        imap_server = config.IMAP_SERVER
        # Подключаемся к IMAP-серверу с предоставленными данными
        imap = imaplib.IMAP4_SSL(imap_server)
        imap.login(user_email, password)
        imap.logout()
        return True
    except:
        return False


def get_new_message(email_address, email_pass) -> list:
    # Получаем логин и пароль от почты для парсинг по imap и возвращаем список с данными о сообщениях

    message_list = []
    imap_server = config.IMAP_SERVER

    # Подключение к серверу IMAP
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(email_address, email_pass)

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
            decoded_subject = decode_header(email_message['Subject'])[0]
            subject_text, encoding = decoded_subject
            subject = ''

            if isinstance(subject_text, bytes):
                subject = subject_text.decode(encoding or 'utf-8')

            if 'your code is' in subject.lower():
                continue

            recipient = email_message['To']

            message_list.append((subject, recipient))

            # Отметка сообщения как прочитанного
            imap.store(num, '+FLAGS', '\\Seen')

        # Завершение работы с сервером IMAP
    imap.logout()

    return message_list


