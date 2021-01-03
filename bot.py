import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot_storage.configuration import telegram_bot_token
import sys

# logging.basicConfig(filename='logs/tatgram_rasp34.log', level=logging.DEBUG)

bot_logger = logging.getLogger()
bot_logger.setLevel(logging.INFO)

bot_logger_handler = logging.StreamHandler(sys.stdout)
bot_logger_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
bot_logger_handler.setFormatter(formatter)
bot_logger.addHandler(bot_logger_handler)

logging.info("BOT START")
# print("BOT START")

API_TOKEN = telegram_bot_token

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
