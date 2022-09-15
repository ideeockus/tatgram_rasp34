from typing import Optional

from bot_storage import configuration

import string
import random
import requests


def progress_bar(percents: int, bar_max_width=10) -> str:
    filled_part = percents//bar_max_width
    empty_part = bar_max_width - filled_part
    return "[" + '#'*filled_part + '  '*empty_part + "]"


def gen_random_string(length: int = configuration.auth_key_default_length) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def send_direct_message(chat_id: str, msg_text: str):
    requests.post(f"https://api.telegram.org/bot{configuration.telegram_bot_token}/sendMessage",
                  data={
                      "chat_id": chat_id,
                      "text": msg_text
                  })


def get_account_human_readable(firstname: Optional[str], lastname: Optional[str],
                               username: Optional[str], user_id: Optional[str]) -> str:
    return (f"{firstname}" if firstname else "") + \
           (f" {lastname}" if lastname else "") + \
           (f" @{username}" if username else "") + \
           (f" [{user_id}]" if user_id else "")
