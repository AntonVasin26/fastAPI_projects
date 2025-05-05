from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Используй относительный путь, если база лежит в корне проекта
SQLALCHEMY_DATABASE_URL = "sqlite:///./new_minimal_db.db"

# Для SQLite обязательно добавлять connect_args={"check_same_thread": False}
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()