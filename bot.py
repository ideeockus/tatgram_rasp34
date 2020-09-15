import ujson
import logging
from aiogram import Bot, Dispatcher, executor, types, utils
from Keyboards import main_kb, teacher_kb
import sys

API_TOKEN = '1286086004:AAHuFMEU6Su4ytCc3ZH-eUAy1ykIi2p3HTM'

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)  # format='%(name)s - %(levelname)s - %(message)s'
# logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def help(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer("Здравствуйте. \n Выберите свою роль")

@dp.message_handler(lambda m: m.text=="")
async def test_handle(message: types.Message):

    if message.text == "Для учителя":
        await message.answer("ок", reply_markup=teacher_kb)
        return
    elif message.text == "Расписание учителей":
        await message.reply("Расписание учителей: *тут распиасние*")
        return

    await message.answer("секундочку...")
    await message.answer(f"{message.text}. понял, дайте подумать", reply_markup=main_kb)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


