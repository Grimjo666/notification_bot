import imaplib
import email
from bot import config


def filter_string(string, str_in, str_not_in):
    # Общая функция для проверки строк
    return (str_in is None or str_in.lower() in string.lower()) and (str_not_in is None or str_not_in.lower() not in string.lower())


def sender_filter(sender, str_in, str_not_in):
    # Функция для фильтрации отправителя по ключевым словам.
    return isinstance(sender, str) and filter_string(sender, str_in, str_not_in)


def subject_filter(subject, str_in, str_not_in):
    # Функция для фильтрации темы сообщения по ключевым словам.
    return isinstance(subject, str) and filter_string(subject, str_in, str_not_in)


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

            # Фильтрация сообщений по отправителю
            if not sender_filter(sender, config.KEYWORD_IN_SENDER, config.KEYWORD_NOT_IN_SENDER):
                continue

            # Извлечение заголовка
            subject = email_message['Subject']

            if not subject_filter(subject, config.KEYWORD_IN_SUBJECT, config.KEYWORD_NOT_IN_SUBJECT):
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


