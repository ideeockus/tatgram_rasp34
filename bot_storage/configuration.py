import os
import re

yadisk_token = os.environ.get('YADISK_TOKEN')
telegram_bot_token = os.environ.get('TG_BOT_TOKEN')
feedback_tg_ids = set(re.findall(r"\d+", os.environ.get('FEEDBACK_TG_IDS') or ""))
db_url = os.environ.get("DATABASE_URL")
botmaster_role_phrase = os.environ.get("BOTMASTER_PHRASE")
allow_broadcasts = bool(int(os.environ.get("ALLOW_BROADCASTS", 0)))

auth_key_default_length = 10


if None in (yadisk_token, telegram_bot_token, feedback_tg_ids, db_url,
            botmaster_role_phrase, allow_broadcasts):
    print("os environments YADISK_TOKEN, TG_BOT_TOKEN, DATABASE_URL,"
          "FEEDBACK_TG_ID, BOTMASTER_PHRASE, ALLOW_BROADCASTS not found")
    raise KeyError
