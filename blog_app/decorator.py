from functools import wraps
from flask import session, flash, redirect, url_for
from blog_app.db.service import UserDatabase

user_db = UserDatabase()

def check_post_owner(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Спочатку увійдіть в систему', 'error')
            return redirect(url_for('login'))

        post_id = kwargs.get('post_id')
        if post_id:
            post = user_db.get_post(post_id)
            if not post:
                flash('Пост не знайдено', 'error')
                return redirect(url_for('my_posts'))

            if post[6] != session['user_id']:  # перевіряємо user_id поста
                flash('У вас немає прав для цієї дії', 'error')
                return redirect(url_for('my_posts'))

        return f(*args, **kwargs)
    return decorated_function