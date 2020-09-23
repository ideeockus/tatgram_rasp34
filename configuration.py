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
        yadisk_token = "AgAAAAAaIF8IAAaapPoVyeBXBkdcmzxtooOnKh0"
        telegram_bot_token = "1286086004:AAHuFMEU6Su4ytCc3ZH-eUAy1ykIi2p3HTM"
        postgresql_db_url = "postgres://auovkhqgqesnwt:fa20dd28eca1d0cdae4bfdc646baef253a99aa3e423ef3fd413ee98abbb195d8@ec2-54-246-85-151.eu-west-1.compute.amazonaws.com:5432/dce3m16p78rm71"
        raise KeyError
except KeyError:
    print("os environments YADISK_TOKEN, TG_BOT_TOKEN, DATABASE_URL not found")
