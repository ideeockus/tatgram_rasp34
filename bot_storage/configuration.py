import os

yadisk_token = ""
telegram_bot_token = ""
# postgresql_db_password = ""
feedback_tg_id = ""
postgresql_db_url = ""

try:
    yadisk_token = os.environ.get('YADISK_TOKEN')
    telegram_bot_token = os.environ.get('TG_BOT_TOKEN')
    feedback_tg_id = os.environ.get('FEEDBACK_TG_ID')
    postgresql_db_url = os.environ.get("DATABASE_URL")
    # if yadisk_token is None or telegram_bot_token is None or postgresql_db_url is None:
    if None in (yadisk_token, telegram_bot_token, feedback_tg_id, postgresql_db_url):
        raise KeyError
except KeyError:
    print("os environments YADISK_TOKEN, TG_BOT_TOKEN, DATABASE_URL, FEEDBACK_TG_ID not found")
