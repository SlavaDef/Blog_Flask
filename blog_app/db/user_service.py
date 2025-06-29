import hashlib
import sqlite3
from typing import Tuple, Optional


class UserDatabase:
    def __init__(self, db_name: str = 'user_blog.db'):
        self.db_name = db_name
        self.create_users_table()


    def create_users_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_aut (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            ''')


    def create_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        if not all([username, email, password]):
            return False, "Всі поля повинні бути заповнені"

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO user_aut (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, password_hash)
                )
                return True, "Користувач успішно створений"
        except sqlite3.IntegrityError:
            return False, "Користувач з таким email вже існує"
        except Exception as e:
            return False, f"Помилка при створенні користувача: {str(e)}"


    def verify_user(self, email: str, password: str) -> Tuple[bool, Optional[dict]]:
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, email FROM user_aut WHERE email = ? AND password_hash = ?",
                    (email, hashlib.sha256(password.encode()).hexdigest())
                )
                user = cursor.fetchone()

                if user:
                    return True, {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2]
                    }
                return False, None
        except Exception as e:
            return False, None


    def select_all(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * from user_aut")
                return cursor.fetchall()
        except sqlite3.IntegrityError:
            return  "Error"
