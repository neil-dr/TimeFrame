import sqlite3
from datetime import datetime

class LogManager:
    def __init__(self, db_path="logs.db"):
        self.db_path = db_path
        self._ensure_table()

    def _get_connection(self):
        # Create a fresh connection per thread
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _ensure_table(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    message TEXT,
                    created_at TEXT
                )
            """)
            conn.commit()

    def insert_question(self, question, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO logs (type, message, created_at) VALUES (?, ?, ?)",
                ("question", question, timestamp)
            )
            conn.commit()

    def insert_error(self, error_message, timestamp=None):
        print(1)
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        print(2)
        with self._get_connection() as conn:
            print(3)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO logs (type, message, created_at) VALUES (?, ?, ?)",
                ("error", error_message, timestamp)
            )
            conn.commit()
