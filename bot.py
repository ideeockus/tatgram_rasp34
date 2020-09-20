import logging
from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from configuration import telegram_bot_token

logging.basicConfig(filename='tatgram_rasp34.log', level=logging.DEBUG)

# API_TOKEN = '1286086004:AAHuFMEU6Su4ytCc3ZH-eUAy1ykIi2p3HTM'
API_TOKEN = telegram_bot_token

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


