import mysql.connector
from datetime import datetime
from config.db import *

# Singleton Metaclass


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


# LogManager Singleton
class LogManager(metaclass=SingletonMeta):
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=HOST,
            user=USERNAME,
            password=PASSWORD,
            database=DB,
            port=PORT
        )
        print("Connected to MYSQL DB")
        self.cursor = self.conn.cursor()
        self.current_question_log_id = None

    def insert_question(self, question: str) -> int:
        query = """
        INSERT INTO logs (event, question, question_timestamp)
        VALUES (%s, %s, %s)
        """
        values = ("question", question, # `datetime.now()` is a method from the `datetime` module in
        # Python that returns the current date and time as a
        # `datetime` object. It does not require any arguments and
        # will return the current date and time at the moment it is
        # called.
        datetime.now())
        self.cursor.execute(query, values)
        self.conn.commit()
        self.current_question_log_id = self.cursor.lastrowid
        return self.cursor.lastrowid

    def insert_error(self, error_message: str) -> int:
        query = """
        INSERT INTO logs (event, error_message, error_timestamp)
        VALUES (%s, %s, %s)
        """
        values = ("error", error_message, datetime.now())
        self.cursor.execute(query, values)
        self.conn.commit()
        return self.cursor.lastrowid

    def update_answer(self, answer: str):
        if self.current_question_log_id is None:
            raise ValueError("No current question to update.")

        query = """
        UPDATE logs
        SET answer = %s,
            answer_timestamp = %s
        WHERE id = %s
        """
        values = (answer, datetime.now(), self.current_question_log_id)
        self.cursor.execute(query, values)
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
