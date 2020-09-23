import logging
from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot_storage.configuration import telegram_bot_token

logging.basicConfig(filename='logs/tatgram_rasp34.log', level=logging.DEBUG)

logging.info("BOT START")
print("BOT START")

API_TOKEN = telegram_bot_token

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


