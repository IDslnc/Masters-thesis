from db.database import engine
from db.models import Base

if __name__ == "__main__":
    print("Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы.")
