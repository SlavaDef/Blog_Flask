import hashlib
import sqlite3
from typing import Tuple, Optional


class UserDatabase:
    def __init__(self, db_name: str = 'user_blog.db'):
        self.db_name = db_name
        self.create_users_table()
        self.create_blogs_table()


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


    def create_blogs_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author TEXT NOT NULL,
                    image_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES user_aut (id)
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


    def insert_post(self, title, content, author, user_id, image_path=None):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO posts (title, content, author, image_path, user_id) 
                    VALUES (?, ?, ?, ?, ?)""",
                    (title, content, author, image_path, user_id)
                )
                return True, "Пост успішно створено"
        except sqlite3.IntegrityError:
            return False, "Помилка: користувача з таким ID не існує"
        except Exception as e:
            return False, f"Помилка при створенні поста: {str(e)}"


    def check_table_structure(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Отримуємо інформацію про структуру таблиці
            cursor.execute("PRAGMA table_info(posts)")
            columns = cursor.fetchall()
            print("Table structure:")
            for col in columns:
                print(f"Column: {col}")


    def select_all_posts(self):
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
            SELECT id, title, content, author, image_path, 
            strftime('%d.%m.%Y %H:%M', datetime(created_at, '+3 hours')) as formatted_date,
            user_id
            FROM posts
            ORDER BY created_at DESC
            """)
                posts = cursor.fetchall()
            return posts


    def get_posts_by_author(self, author: str):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, title, content, author, image_path,
                    strftime('%d.%m.%Y %H:%M', datetime(created_at, '+3 hours')) as formatted_date,
                    user_id
                    FROM posts 
                    WHERE author = ?
                    ORDER BY created_at DESC
                """, (author,))
                posts = cursor.fetchall()
                return posts
        except Exception as e:
            print(f'Помилка при отриманні постів автора: {e}')
            return []


    def get_post(self, post_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                            SELECT id, title, content, author, image_path, 
                            strftime('%d.%m.%Y %H:%M', datetime(created_at, '+3 hours')) as formatted_date,
                            user_id FROM posts WHERE id = ?""", (post_id,))
                post = cursor.fetchone()
                return post if post else None
        except Exception as e:
            print(f'Error getting post: {e}')
            raise


    def update_post(self, post_id, title, content, image_path=None):

        try:
              with sqlite3.connect(self.db_name) as conn:
                  cursor = conn.cursor()
                # Якщо нове фото не завантажене, зберігаємо існуюче
                  if image_path is None:
                      cursor.execute('SELECT image_path FROM posts WHERE id = ?', (post_id,))
                      result = cursor.fetchone()
                      if result:
                          image_path = result[0]

                  cursor.execute('''
                   UPDATE posts 
                   SET title = ?, content = ?, image_path = ? 
                   WHERE id = ?
               ''', (title, content, image_path, post_id))
              return cursor.rowcount > 0  # Оновлення успішне

        except Exception as e:
            raise Exception(f"Помилка бази даних: {str(e)}")


    def delete_post(self, post_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        except sqlite3.Error as e:
            raise Exception(f"Помилка бази даних: {str(e)}")