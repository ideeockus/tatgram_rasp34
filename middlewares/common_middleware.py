from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler, current_handler

# мидлвари обрабатывают кадое сообщение
from bot_storage import accounts_base
from bot_storage.accounts_base import Roles


class CommonMiddleware(BaseMiddleware):

    async def on_process_message(self, message: types.Message, data: dict):
        user_id = message.from_user.id
        username = message.from_user.username
        role = accounts_base.get_role(user_id) or Roles.guest

        print(f"Message from {role.name} @{username}[{user_id}]")
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        pass

        # print("handler", handler)
        # print("dispatcher", dispatcher)


# class RolesMiddleware(BaseMiddleware):
#     async def on_process_message(self, message: types.Message, data: dict):
#         user_id = message.from_user.id
#         data["role"] = "Unknonw l"

