import imaplib
import email


# Параметры подключения к серверу Gmail
def get_new_message(username, mail_pass):
    message_list = []
    imap_server = 'imap.mail.ru.'

    # Подключение к серверу IMAP
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, mail_pass)

    for elem in ('INBOX', 'INBOX/Newsletters'):
        # Выбор почтового ящика
        imap.select(elem)

        # Поиск непрочитанных сообщений
        typ, msg_nums = imap.search(None, 'UNSEEN')

        # Обработка каждого найденного сообщения
        for num in msg_nums[0].split():
            # Получение сообщения по его номеру
            typ, msg_data = imap.fetch(num, '(RFC822)')
            raw_email = msg_data[0][1]

            # Парсинг сообщения
            email_message = email.message_from_bytes(raw_email)

            sender = email_message['From']
            if isinstance(sender, str) and 'fansly' not in sender.lower():
                continue

            # Извлечение заголовка
            subject = email_message['Subject']

            if isinstance(subject, str) and 'your code is' in subject.lower():
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
