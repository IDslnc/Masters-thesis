from db.database import SessionLocal
from db.models import User

db = SessionLocal()

user = User(
    full_name="Шляпик Александр Александрович",
    login="sasha",
    password_hash="228",  # Пока без хеширования
    user_role="администратор"
)

db.add(user)
db.commit()
print("Пользователь добавлен.")
