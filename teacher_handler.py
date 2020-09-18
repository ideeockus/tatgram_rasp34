import ujson
import logging
from aiogram import Bot, Dispatcher, executor, types, utils
from Keyboards import pupil_kb, teacher_kb, choose_role_kb
import sys
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from rasp_base import get_lessons, get_lessons_for_today, get_lessons_for_yesterday
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime
from bot import dp, bot
import yadisk
from configuration import yadisk_token
from Keyboards import teacher_photo_sending_kb, teacher_kb

y = yadisk.YaDisk(token=yadisk_token)


class TeacherStates(StatesGroup):
    rasp_today = State()  # расписание на сегодня
    rasp_yesterday = State()  # расписание на завтра
    waiting_for_action = State()  # ожидание действий
    waiting_for_identifier = State()  # ждет имя
    waiting_for_photo = State()


@dp.message_handler(lambda m: m.text == "Расписание учителей", state=TeacherStates.waiting_for_action)
async def rasp_yesterday(message: types.Message, state: FSMContext):
    print("Запрос расписания учителей")
    await message.reply("В базе данных пока нет информации об учителях")


@dp.message_handler(lambda m: m.text == "Отправить фото", state=TeacherStates.waiting_for_action, content_types=types.ContentType.TEXT)
async def rasp_today(message: types.Message, state: FSMContext):
    print("пользователь хочет прислать фото")
    await message.answer("Пожалуйста, отправьте фотографию", reply_markup=teacher_photo_sending_kb)
    await TeacherStates.waiting_for_photo.set()


@dp.message_handler(lambda m: m.text == "Назад (отправка фото окончена)", state=TeacherStates.waiting_for_photo)
async def rasp_today(message: types.Message, state: FSMContext):
    print("отправка фото закончена")
    await message.answer("Отлично", reply_markup=teacher_kb)
    await TeacherStates.waiting_for_action.set()


@dp.message_handler(state=TeacherStates.waiting_for_photo, content_types=types.ContentType.TEXT)
async def wait_for_photo_got_text(message: types.Message):
    await message.reply("Круто, но я все еще жду фото")


@dp.message_handler(state=TeacherStates.waiting_for_photo, content_types=types.ContentType.PHOTO)
async def rasp_today(message: types.Message, state: FSMContext):
    print("Принимаю фото")
    photo = message.photo
    print(photo)
    await message.photo[-1].download("files/photo"+str(datetime.now()))

    # file_name = message.document.file_name
    await message.reply("Готово")


@dp.message_handler(state=TeacherStates.waiting_for_photo, content_types=types.ContentType.DOCUMENT)
async def rasp_today(message: types.Message, state: FSMContext):
    print("Принимаю документ")
    file_id = message.document.file_id
    file_name = message.document.file_name

    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "files/" + file_name)
    await message.reply("Готово, документ оправлен")





