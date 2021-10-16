from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class RoleRecord(Base):
    """Модель ДБ старой версии бота"""
    __tablename__ = "roles_db"
    # id = Column(Integer)
    user_id = Column(String, primary_key=True)
    role = Column(String)
    identifier = Column(String)  # идентификатор
    class_name = Column(String)  # имя класса
    teacher_name = Column(String)  # имя учителя
    username = Column(String)
    user_fullname = Column(String)
    registration_date = Column(DateTime)
    # registration_date = Column(String)  # del


DB_URL = "sqlite:////mnt/windows_files/FILES/projects/school34_bot/test_dbs/db1"
engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)


def up_classes_old():
    """Поднять классы на один вверх"""
    roles_db_session = Session()
    user_records = roles_db_session.query(RoleRecord).all()

    for user_record in user_records:
        old_class = user_record.class_name
        if old_class is None:
            continue
        new_class_num = old_class[0:-1]
        new_class_symb = old_class[-1]
        if not new_class_num.isdigit() or new_class_symb.isdigit():
            raise Exception("class name error")
        new_class_num = int(new_class_num) + 1
        new_class_name = str(new_class_num) + new_class_symb
        if new_class_num >= 12:
            continue
        print(f"{old_class} -> {new_class_name}")
        user_record.class_name = new_class_name

    roles_db_session.commit()
    roles_db_session.close()


if __name__ == "__main__":
    print("Migrating user records db")
    up_classes_old()
    print("Done")

