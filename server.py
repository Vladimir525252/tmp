import os
import bcrypt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base

# --- КОНФИГУРАЦИЯ ---
# В Render эти переменные берутся из панели Environment Variables
DATABASE_URL = os.getenv("DATABASE_URL")
# Если на Render нет переменной, по умолчанию будет локальный файл (для тестов)

app = FastAPI()
Base = declarative_base()


# --- МОДЕЛЬ ДАННЫХ ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)


# Настройка БД
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем таблицы при старте (в продакшене лучше использовать миграции)
Base.metadata.create_all(bind=engine)


# --- СХЕМЫ ДАННЫХ (Pydantic) ---
class AuthRequest(BaseModel):
    state: str  # 'reg' или 'log'
    email: str
    name: str
    psw: str


# --- ЛОГИКА ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/auth")
def authenticate(request: AuthRequest):
    db = next(get_db())

    if request.state == 'reg':
        # ПРОВЕРКА: существует ли уже такой пользователь
        existing_user = db.query(User).filter(
            (User.email == request.email) | (User.name == request.name)
        ).first()

        if existing_user:
            return {"success": False, "message": "Пользователь с таким email или именем уже существует"}

        # РЕГИСТРАЦИЯ: хешируем пароль перед сохранением!
        # bcrypt автоматически добавляет соль
        hashed_password = bcrypt.hashpw(request.psw.encode('utf-8'), bcrypt.gensalt())

        new_user = User(name=request.name, email=request.email, password_hash=hashed_password.decode('utf-8'))
        db.add(new_user)
        db.commit()
        return {"success": True, "message": "Регистрация успешна"}

    elif request.state == 'log':
        # ВХОД: ищем пользователя по email (или name, зависит от логики входа)
        # Обычно вход делают по email, а name - это просто отображаемое имя
        user = db.query(User).filter(User.email == request.email).first()

        if not user:
            return {"success": False, "message": "Пользователь не найден"}

        # ПРОВЕРКА ПАРОЛЯ: сравниваем введенный пароль с хешем из БД
        # Это гарантирует, что psw проверяется только для этой конкретной строки (пользователя)
        if bcrypt.checkpw(request.psw.encode('utf-8'), user.password_hash.encode('utf-8')):
            return {"success": True, "message": "Вход выполнен"}
        else:
            return {"success": False, "message": "Неверный пароль"}

    else:
        raise HTTPException(status_code=400, detail="Неверное значение state. Должно быть 'reg' или 'log'")


if __name__ == "__main__":
    import uvicorn

    # Для Render не запускай через __main__, он сам вызовет uvicorn через Procfile или настройки
    uvicorn.run(app, host="0.0.0.0", port=8000)
