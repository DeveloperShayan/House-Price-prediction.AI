import pyodbc


def list_sql_server_drivers():
    drivers = pyodbc.drivers()
    print("Installed ODBC drivers:")
    for driver in drivers:
        print(f"- {driver}")

    sql_server_drivers = [d for d in drivers if "SQL Server" in d]
    if sql_server_drivers:
        print("\nAvailable SQL Server drivers:")
        for driver in sql_server_drivers:
            print(f"- {driver}")
    else:
        print("\nNo SQL Server ODBC driver found.")


if __name__ == "__main__":
    list_sql_server_drivers()
