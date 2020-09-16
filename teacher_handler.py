import ujson
import logging
from aiogram import Bot, Dispatcher, executor, types, utils
from Keyboards import pupil_kb, teacher_kb, choose_role_kb
import sys
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from rasp_base import get_lessons, get_lessons_for_today, get_lessons_for_yesterday
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot import dp


class TeacherStates(StatesGroup):
    rasp_today = State()  # расписание на сегодня
    rasp_yesterday = State()  # расписание на завтра
    waiting_for_action = State()  # ожидание действий
    waiting_for_identifier = State()  # ждет имя