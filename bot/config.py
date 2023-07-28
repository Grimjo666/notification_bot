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

