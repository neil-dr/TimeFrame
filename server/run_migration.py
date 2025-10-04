import mysql.connector
from config.db import *

def run_migration():
    # Read migration SQL
    with open("migrations/migration.sql", "r") as f:
        sql = f.read()

    # Connect without specifying database (to create schema if needed)
    conn = mysql.connector.connect(
        host=HOST,
        user=USERNAME,
        password=PASSWORD
    )

    cursor = conn.cursor()

    # Create schema if not exists
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {DB}")

    # Switch to the created schema
    cursor.execute(f"USE {DB}")

    # Run migration SQL (e.g. table creation)
    cursor.execute(sql)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    run_migration()
