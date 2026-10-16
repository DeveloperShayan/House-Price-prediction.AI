from sqlalchemy import text

from app.database.connection import engine, PROJECT_DATABASE


def check_or_create_database():
    try:
        # AUTOCOMMIT is required because CREATE DATABASE can't run inside a transaction
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            exists = connection.execute(
                text("SELECT database_id FROM sys.databases WHERE name = :name"),
                {"name": PROJECT_DATABASE},
            ).scalar() is not None

            if exists:
                print(f"Database '{PROJECT_DATABASE}' already exists.")
            else:
                connection.execute(text(f"CREATE DATABASE [{PROJECT_DATABASE}]"))
                print(f"Database '{PROJECT_DATABASE}' created successfully!")
    except Exception as error:
        print("Failed to check/create the database.")
        print(error)
    finally:
        engine.dispose()


if __name__ == "__main__":
    check_or_create_database()
