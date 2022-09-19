## Telegram bot for school
_This project will be present on International Forum_
[Kazan Digital Week 2022](https://kazandigitalweek.com/en/site)

This bot hepls to view the school schedule and order food.

Bot has a role system.

Also, it can send reports in case of error occurred.

### Features of various roles:

##### Administrator:

- Brroadcasting by groups or to p2p
- Uploading schoool timetable
- Uploading a list of students and teachers
for whom a unique login key will be generated
- Uploading the menu for ordering food
- View student/teacher schedules
- View statistics

##### Student/Parent/Class leader:

- View the schedule
- Ordering food
- Sending feedback

##### Teacher
- View schedules
- Uploading documents to Yandex.Disk
- Sending feedback

##### Nutrition Manager

- Food order management (view/clean)
- Sending feedback

## Configuration
Configuration is performed using env vars.
This is convenient when running as a systemd-unit or in a container.

**YADISK_TOKEN** - token for Yandex.Disk API.
**TG_BOT_TOKEN** - Telegram bot API token.
**FEEDBACK_TG_IDS** - Telegram IDs of persons who will receive feedbacks and error reports
**DATABASE_URL** - Database URL. Tested with PostgreSQL and SQLite.
**ALLOW_BROADCASTS** -  Set 1 to allow broadcasts from administrator role.

## Installation
Установка зависимостей
```
python3 -m pip install -r requirements.txt
```

Запуск
```
python3 main.py
```

