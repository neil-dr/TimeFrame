import sqlite3
from datetime import datetime
from pathlib import Path

# Singleton Metaclass
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


# LogManager Singleton using SQLite
class LogManager(metaclass=SingletonMeta):
    def __init__(self, db_path: str = "timeframe_logs.db"):
        """Initialize SQLite connection and ensure logs table exists."""
        db_file = Path(db_path)
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        print(f"Connected to SQLite DB at {db_file.resolve()}")
        self.current_question_log_id = None

        # Create table if it doesn't exist
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            question TEXT,
            question_timestamp TEXT,
            answer TEXT,
            answer_timestamp TEXT,
            error_message TEXT,
            error_timestamp TEXT
        )
        """)
        self.conn.commit()

    def insert_question(self, question: str) -> int:
        query = """
        INSERT INTO logs (event, question, question_timestamp)
        VALUES (?, ?, ?)
        """
        values = ("question", question, datetime.now().isoformat())
        self.cursor.execute(query, values)
        self.conn.commit()
        self.current_question_log_id = self.cursor.lastrowid
        return self.cursor.lastrowid

    def insert_error(self, error_message: str) -> int:
        query = """
        INSERT INTO logs (event, error_message, error_timestamp)
        VALUES (?, ?, ?)
        """
        values = ("error", error_message, datetime.now().isoformat())
        self.cursor.execute(query, values)
        self.conn.commit()
        return self.cursor.lastrowid

    def update_answer(self, answer: str):
        if self.current_question_log_id is None:
            raise ValueError("No current question to update.")

        query = """
        UPDATE logs
        SET answer = ?,
            answer_timestamp = ?
        WHERE id = ?
        """
        values = (answer, datetime.now().isoformat(), self.current_question_log_id)
        self.cursor.execute(query, values)
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
