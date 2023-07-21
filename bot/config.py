from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

BOT_TOKEN = os.getenv('BOT_TOKEN')
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASS = os.getenv('EMAIL_PASS')
# Кортеж с папками для парсинга почты
EMAIL_FOLDERS = ('INBOX', 'INBOX/Newsletters')
IMAP_SERVER = 'imap.mail.ru.'
IMAP_CRITERIA = 'UNSEEN'

#  Ключевые слова для фильтрации отправителя и темы сообщения
KEYWORD_IN_SENDER = 'fansly'  # Проверяем есть ли строка в заголовке (если есть заголовок прошёл проверку)
KEYWORD_NOT_IN_SENDER = None  # Проверяем нет ли строки в заголовке (если нет заголовок прошёл проверку)

KEYWORD_IN_SUBJECT = None
KEYWORD_NOT_IN_SUBJECT = 'your code is'
