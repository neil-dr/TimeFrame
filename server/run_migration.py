import mysql.connector
from config.db import *

def run_migration():
    with open("migrations/migration.sql", "r") as f:
        sql = f.read()

    conn = mysql.connector.connect(
        host=HOST,
        user=USERNAME,
        password=PASSWORD,
        database=DB
    )

    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    print("Migration completed.")


if __name__ == "__main__":
    run_migration()
