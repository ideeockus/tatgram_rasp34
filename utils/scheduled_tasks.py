from datetime import datetime, timedelta
from typing import Callable

from aiogram import Bot
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound

from bot_storage import bot_stats
from bot import bot

import sched
import asyncio

from bot_storage.UserStates import get_role_waiting_for_action_state
from bot_storage.roles_base import get_role

# class ScheduledTask:
#     def __init__(self, task_datetime: datetime, priority: int, task_func: Callable, task_kwargs: dict):
#         seconds_until_task_execution = (task_datetime-datetime.now()).seconds
#         self.scheduler = sched.scheduler()
#         self.scheduler.enter(seconds_until_task_execution, priority, task_func, kwargs=task_kwargs)
#
#     def run_task(self):
#         self.scheduler.run()
#
# asyncio.get_event_loop().call_at()


def set_midnight_stats_clear_task():
    """
    Чистить статистику в полночь каждого дня
    :return:
    """

    print("Очистка статистики в", datetime.now().isoformat())
    bot_stats.clean_stats(bot_stats.StatsType.ByClass)

    current_dt = datetime.now()
    midnight_dt = datetime(current_dt.year, current_dt.month, current_dt.day, 23, 59, 59)
    # midnight_dt = datetime(current_dt.year, current_dt.month, current_dt.day, 1, 20, 00)
    seconds_until_midnight = (midnight_dt - datetime.now()).seconds
    if seconds_until_midnight <= 5:  # если осталось меньше 5 секунд
        seconds_until_midnight = 86400
    print("Следующая очистка статистики запланирована на",
          (datetime.now() + timedelta(seconds=seconds_until_midnight)).isoformat())

    asyncio.get_event_loop().call_later(seconds_until_midnight, set_midnight_stats_clear_task)


def set_weakly_stats_clear_task(clean_on_start=True):
    """
    Чистить статистику в каждую неделю
    :return:
    """

    # def clean_stat_and_reset_task():
    if clean_on_start:
        print("Очистка статистики в", datetime.now().isoformat())
        bot_stats.clean_stats(bot_stats.StatsType.ByClass)

    current_dt = datetime.now()
    # print("weekday", current_dt.weekday())
    # stat_clean_dt = datetime(current_dt.year, current_dt.month, current_dt.day, 23, 59, 59)
    stat_clean_dt = current_dt.replace(hour=23, minute=59, second=59) + timedelta(days=6-current_dt.weekday())
    # print("clean date", stat_clean_dt)
    seconds_until_clean = (stat_clean_dt - datetime.now()).total_seconds()
    # print("sec unt clean", seconds_until_clean)
    if seconds_until_clean <= 5:  # если осталось меньше 5 секунд
        seconds_until_clean = 86400*7
    print("Следующая очистка статистики запланирована на",
          (datetime.now() + timedelta(seconds=seconds_until_clean)).isoformat())

    asyncio.get_event_loop().call_later(seconds_until_clean, set_midnight_stats_clear_task)


def set_message_timeout(chat_id: int, message_id: int, message_timeout=10):
    def del_msg():
        asyncio.ensure_future(bot.delete_message(chat_id=chat_id, message_id=message_id))

    asyncio.get_event_loop().call_later(message_timeout, del_msg)


def set_message_timeout_and_reset_state(user_id: int, chat_id: int, message_id: int, message_timeout=10):
    #  TODO: add user_state: FSMContext arg with set_state()
    """
    Сейчас вызывается только в текущем контексте
    :param user_id:
    :param chat_id:
    :param message_id:
    :param message_timeout:
    :return:
    """
    # def del_msg():
    #     # def bot_del_msg_with_catch():
    #     #     try:
    #     #         bot.delete_message(chat_id=chat_id, message_id=message_id)
    #     #     except MessageToDeleteNotFound:
    #     #         pass  # сообщения уже нет, скорее всего оно уже было удалено
    #
    #     user_role = get_role(user_id)
    #     print(f"Deleting message {chat_id}_{message_id} by timeout")
    #     print(f"User role is {user_role}. Reset state")
    #     try:
    #         asyncio.ensure_future(bot.delete_message(chat_id=chat_id, message_id=message_id))
    #         asyncio.ensure_future(get_role_waiting_for_action_state(user_role).set())
    #     except MessageToDeleteNotFound:
    #         print("Message for deletion was not found")

    async def del_msg():
        user_role = get_role(user_id)
        try:
            print(f"Deleting message {chat_id}_{message_id} by timeout")
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
            # если при удалении выкинулось исключение
            # то состояние пользователя не будет сброшено
            print(f"User role is {user_role}. Reset state")
            await get_role_waiting_for_action_state(user_role).set()
        except MessageToDeleteNotFound:
            print("Message for deletion was not found")

    asyncio.get_event_loop().call_later(message_timeout, lambda: asyncio.ensure_future(del_msg()))

