from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Подключение к PostgreSQL (замени логин/пароль/БД)
DATABASE_URL = "postgresql://postgres:admin123@localhost:5432/dental_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()