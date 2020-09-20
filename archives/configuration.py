import os

yadisk_token = ""
telegram_bot_token = ""
postgresql_db_password = ""
postgresql_db_url = ""


try:
    yadisk_token = os.environ.get('YADISK_TOKEN')
    telegram_bot_token = os.environ.get('TG_BOT_TOKEN')
    # postgresql_db_password = os.environ.get('PGSQL_DB_PASSWORD')
    postgresql_db_url = os.environ.get("DATABASE_URL")
    if yadisk_token is None or telegram_bot_token is None or postgresql_db_url is None:
        raise KeyError
except KeyError:
    print("os environments YADISK_TOKEN, TG_BOT_TOKEN, DATABASE_URL not found")
