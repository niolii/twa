import aiogram
import dotenv
import os
import json

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telethon.sync import TelegramClient
from db.db_editor import DBEditor

dotenv.load_dotenv()


if not os.path.exists('images'):
    os.mkdir('images')

token = os.getenv('BOT_TOKEN')
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_link = os.getenv('BOT_LINK')
parser_account_id = int(os.getenv('PARSER_ACCOUNT'))
admins = json.loads(os.getenv('ADMINS'))

bundles = []
if os.path.exists('bundles.json'):
    with open('bundles.json', 'r', encoding='utf-8') as f:
        js = json.loads(f.read())
        bundles.extend(js['bundles'])
with open('project_information.txt', 'r', encoding='utf-8') as f:
    project_info = f.read()
with open('user_guide.txt', 'r', encoding='utf-8') as f:
    user_guide = f.read()

bot = aiogram.Bot(token)
dp = aiogram.Dispatcher(bot, storage=MemoryStorage())
client = TelegramClient('session', api_id, api_hash)
db = DBEditor('base.db')

