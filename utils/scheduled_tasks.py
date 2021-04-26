from datetime import datetime, timedelta
from typing import Callable
from bot_storage import bot_stats

import sched
import asyncio


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
    print("Очистка статистики в", datetime.now().isoformat())
    if clean_on_start:
        bot_stats.clean_stats(bot_stats.StatsType.ByClass)

    current_dt = datetime.now()
    stat_clean_dt = datetime(current_dt.year, current_dt.month, current_dt.day-current_dt.weekday(), 23, 59, 59)
    seconds_until_clean = (stat_clean_dt - datetime.now()).seconds
    if seconds_until_clean <= 5:  # если осталось меньше 5 секунд
        seconds_until_midnight = 86400*7
    print("Следующая очистка статистики запланирована на",
          (datetime.now() + timedelta(seconds=seconds_until_clean)).isoformat())

    asyncio.get_event_loop().call_later(seconds_until_clean, set_midnight_stats_clear_task)
