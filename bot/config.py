from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

BOT_TOKEN = os.getenv('BOT_TOKEN')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
# Кортеж с папками для парсинга почты
EMAIL_FOLDERS = ('INBOX', 'INBOX/Newsletters')
IMAP_SERVER = 'imap.mail.ru.'
IMAP_CRITERIA = 'UNSEEN'

subscribe_dict = {'cripto': 'Оплата переводом на криптокошелёк',
                  'bank': 'Оплата банковским переводом',
                  'base_subscription': 'Базовая (3 аккаунта Телеграм, 6 аккаунтов Fansly)',
                  'extended_subscription': 'Расширенная (6 аккаунта Телеграм, 15 аккаунтов Fansly)',
                  'without_limits': 'Без ограничений',
                  'individual_subscription': 'Индивидуальная (2 аккаунта Телеграм, 1 аккаунт Fansly)'}

subscribe_type_dict = {'base_subscription': (3, 6),
                       'extended_subscription': (6, 15),
                       'without_limits': (100, 200),
                       'individual_subscription': (2, 1)}

subscribe_type_rus_to_eng = {'Базовая подписка': 'base_subscription',
                             'Расширенная подписка':  'extended_subscription',
                             'Без ограничений': 'without_limits',
                             '1 Fansly аккаунт': 'individual_subscription'}
