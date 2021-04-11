from datetime import datetime, timedelta
# from collections.abc import Callable
from asyncio import Future, Task, create_task, AbstractEventLoop
from typing import Callable, Optional
import asyncio

from actions.notify_admins import notify_admins


# """
# Думаю нужно создавать пулы потоков для этих штук
# """
#
#
# class PeriodicOperation:
#     """
#     Действия которые выполняются в каких-либо временных отрезках
#     """
#     def __init__(self, el: AbstractEventLoop, start_date: Optional[datetime], stop_date: Optional[datetime],
#                  do_every_sec: int, do_task: Task, delay_sec: int = 3600):
#         """
#         :param start_date: с какого момента действие начнет выполняться
#         :param stop_date: до какого момента
#         :param do_every_sec: выполнять каждые n сек
#         :param do_func: функция которую выполнять
#         :param delay_sec: задержка во время ожидания даты начала
#         """
#         self.el = el
#         print(self.el)
#         self.start_date = start_date
#         self.stop_date = stop_date
#         self.do_every_sec = do_every_sec
#         # self.do_func = do_func
#         self.do_task = do_task
#         self.delay_sec = delay_sec
#
#         self.do_periodic_operation()
#
#     def do_periodic_operation(self):
#         if self.start_date is None:
#             self.start_date = datetime.now()
#
#         while datetime.now() < self.start_date:
#             asyncio.sleep(self.delay_sec)
#
#         while True:
#             try:
#                 if self.stop_date is None or self.stop_date > datetime.now():
#                     self.el.create_task(self.do_task)
#                     asyncio.sleep(self.do_every_sec)
#             except Exception as e:
#                 print(e)
#                 break


# def run_test_operations():
#     async def do_func():
#         await notify_admins(f"{datetime.now()}")
#     po = PeriodicOperation(None, None, 15, create_task(do_func()))
#     print(po)


async def do_periodic_operation(start_date: Optional[datetime], stop_date: Optional[datetime],
                                do_every_sec: int, do_task: Callable, delay_sec: int = 35):
    """
    :param start_date: с какого момента действие начнет выполняться
    :param stop_date: до какого момента
    :param do_every_sec: выполнять каждые n сек
    :param do_task: функция которую выполнять
    :param delay_sec: задержка во время ожидания даты начала
    """
    # print("start")
    if start_date is None:
        start_date = datetime.now()

    while datetime.now() < start_date:
        # print("sleep for", delay_sec)
        await asyncio.sleep(delay_sec)

    while True:
        try:
            if stop_date is None or stop_date > datetime.now():
                await do_task()
                # print("sleep for", do_every_sec)
                await asyncio.sleep(do_every_sec)
        except Exception as e:
            print(e)
            break
    # print("end")
