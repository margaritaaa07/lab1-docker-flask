import os
import time
from datetime import datetime

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError


# ---------- Чтение переменных окружения ----------
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    raise RuntimeError(
        "Не заданы обязательные переменные окружения: "
        "DB_USER, DB_PASSWORD, DB_HOST, DB_NAME"
    )


# ---------- Flask и БД ----------
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------- Модель ----------
class Visit(db.Model):
    __tablename__ = "visits"

    id = db.Column(db.Integer, primary_key=True)
    visited_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=False)


# ---------- Маршрут ----------
@app.route("/hello")
def hello():
    visit = Visit(
        visited_at=datetime.utcnow(),
        ip_address=request.remote_addr,
    )
    db.session.add(visit)
    db.session.commit()
    return "Hello", 200


# ---------- Создание таблицы с повторными попытками ----------
def init_db(retries: int = 10, delay: float = 2.0) -> None:
    """Создаёт таблицы, повторяя попытки, пока БД не будет готова."""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            with app.app_context():
                db.create_all()
                db.engine.dispose()
            print(f"[init_db] Таблицы созданы (попытка {attempt}).")
            return
        except OperationalError as exc:
            last_error = exc
            print(f"[init_db] БД ещё не готова (попытка {attempt}/{retries}). "
                  f"Ждём {delay} с...")
            time.sleep(delay)
    raise RuntimeError(f"Не удалось инициализировать БД: {last_error}")


# ---------- Инициализация БД при импорте (нужно для gunicorn) ----------
init_db()


# ---------- Точка входа ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)