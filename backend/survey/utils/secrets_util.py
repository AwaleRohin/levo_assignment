import os


def environment():
    return os.getenv("PROFILE", "dev")


def get_db_url():
    return os.getenv("DATABASE_URL", "sqlite:///survey.db")
