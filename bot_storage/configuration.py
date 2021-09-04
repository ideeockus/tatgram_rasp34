import os

# yadisk_token = ""
# telegram_bot_token = ""
# # postgresql_db_password = ""
# feedback_tg_id = ""
# db_url = ""
# botmaster_role_phrase = ""
# allow_broadcasts = ""

yadisk_token = os.environ.get('YADISK_TOKEN')
telegram_bot_token = os.environ.get('TG_BOT_TOKEN')
feedback_tg_id = os.environ.get('FEEDBACK_TG_ID')
db_url = os.environ.get("DATABASE_URL")
db_url = "postgresql://postgres@localhost/test_ps_db"
# db_url = "sqlite:///test_dbs/db3"
botmaster_role_phrase = os.environ.get("BOTMASTER_PHRASE")
allow_broadcasts = bool(int(os.environ.get("ALLOW_BROADCASTS", 0)))

creator_id = "173964659"
auth_key_default_length = 10


if None in (yadisk_token, telegram_bot_token, feedback_tg_id, db_url,
            botmaster_role_phrase, allow_broadcasts):
    print("os environments YADISK_TOKEN, TG_BOT_TOKEN, DATABASE_URL,"
          "FEEDBACK_TG_ID, BOTMASTER_PHRASE, ALLOW_BROADCASTS not found")
    raise KeyError

# try:
#     yadisk_token = os.environ.get('YADISK_TOKEN')
#     telegram_bot_token = os.environ.get('TG_BOT_TOKEN')
#     feedback_tg_id = os.environ.get('FEEDBACK_TG_ID')
#     db_url = os.environ.get("DATABASE_URL")
#     botmaster_role_phrase = os.environ.get("BOTMASTER_PHRASE")
#     allow_broadcasts = bool(int(os.environ.get("ALLOW_BROADCASTS", 0)))
#
#     if None in (yadisk_token, telegram_bot_token, feedback_tg_id, db_url,
#                 botmaster_role_phrase, allow_broadcasts):
#         raise KeyError
# except KeyError:
#     print("os environments YADISK_TOKEN, TG_BOT_TOKEN, DATABASE_URL,"
#           "FEEDBACK_TG_ID, BOTMASTER_PHRASE, ALLOW_BROADCASTS not found")
