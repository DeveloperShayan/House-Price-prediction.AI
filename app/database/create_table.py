from sqlalchemy import create_engine

from app.database.connection import build_url, PROJECT_DATABASE
from app.database.models import Base

engine = create_engine(build_url(PROJECT_DATABASE), pool_pre_ping=True)


def create_table():
    try:
        Base.metadata.create_all(bind=engine)
        print(f"Tables created successfully in '{PROJECT_DATABASE}'!")
    except Exception as error:
        print("Failed to create tables.")
        print("Error:", error)
    finally:
        engine.dispose()


if __name__ == "__main__":
    create_table()
