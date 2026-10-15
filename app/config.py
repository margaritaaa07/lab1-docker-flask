import os

class Config:
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    DB_USER = os.environ.get("DB_USER", "app")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "changeme")
    DB_NAME = os.environ.get("DB_NAME", "visits_db")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False