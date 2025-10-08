import sqlite3
from datetime import datetime
from threading import Lock
class SingletonMeta(type):
    _instances = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class LogManager(metaclass=SingletonMeta):
    def __init__(self, db_path="logs.db"):
        self.db_path = db_path
        self.current_question_log_id = None
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
                    answer TEXT,
                    created_at TEXT,
                    answer_timestamp TEXT
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
            self.current_question_log_id = cursor.lastrowid
            conn.commit()
        return self.current_question_log_id

    def insert_error(self, error_message, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO logs (type, message, created_at) VALUES (?, ?, ?)",
                ("error", error_message, timestamp)
            )
            conn.commit()

    def update_answer(self, answer):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE logs
                SET answer = ?, answer_timestamp = ?
                WHERE id = ?
            """, (answer, datetime.now().isoformat(), self.current_question_log_id))
            conn.commit()

    def close(self):
        """Nothing to close (connections are context-managed), but kept for API consistency."""
        pass
