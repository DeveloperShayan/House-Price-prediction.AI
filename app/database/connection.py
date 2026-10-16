from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# ================================================================
# CHANGE THIS LINE to your own SQL Server name.
# Find it in SSMS: it's the "Server name" shown when you connect.
# Examples: r"localhost\SQLEXPRESS"  or  r"DESKTOP-ABC123\SQLEXPRESS"
SERVER = r"(localdb)\MSSQLLocalDB"
# ================================================================

DATABASE = "master"
PROJECT_DATABASE = "MyFirstAPI"
DRIVER = "ODBC Driver 17 for SQL Server"


def build_url(database: str) -> URL:
    return URL.create(
        "mssql+pyodbc",
        host=SERVER,
        database=database,
        query={
            "driver": DRIVER,
            "trusted_connection": "yes",
            "TrustServerCertificate": "yes",
        },
    )


# Engine connected to "master" (used to check / create the project database)
engine = create_engine(build_url(DATABASE), pool_pre_ping=True)


def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.exec_driver_sql("SELECT @@SERVERNAME")
            print("Connected to SQL Server successfully!")
            print("SQL Server:", result.scalar())
    except Exception as error:
        print("Database connection failed.")
        print(error)
    finally:
        engine.dispose()


if __name__ == "__main__":
    test_connection()
