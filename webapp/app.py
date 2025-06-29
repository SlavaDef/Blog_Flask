import os

from flask import render_template, Flask, request, session, flash, redirect, url_for

from blog_app.db.photo_safer import save_image
from blog_app.db.user_service import UserDatabase
from datetime import datetime
import html

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Обмеження розміру файлу (16MB)
app.secret_key = os.urandom(24) # без ключа сесії не працюють


user_db = UserDatabase()
#user_db.check_table_structure()

@app.route('/')
def main_page():
    return render_template('main.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    success, message = user_db.create_user(username, email, password)

    if success:
        flash('Реєстрація успішна!', 'success')
        return redirect(url_for('profile'))
    else:
        flash(message, 'error')
        return render_template('register.html')


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Спочатку увійдіть в систему натиснувши Login', 'error')
        return redirect(url_for('register'))
    return render_template('profile.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    password = request.form.get('password')

    success, user = user_db.verify_user(email, password)

    if success:
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash('Ви успішно увійшли!', 'success')
        return redirect(url_for('profile'))
    else:
        flash('Невірний email або пароль', 'error')
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Ви вийшли з системи', 'info')
    return redirect(url_for('login'))


@app.route('/new_post', methods=['POST', 'GET'])
def create_post() -> 'html':
    # Перевіряємо авторизацію
    if 'user_id' not in session:
        flash('Спочатку увійдіть в систему для створення поста', 'error')
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('new_post.html')

    title = str(request.form['title'])
    some_text = str(request.form['some_text'])
    # Беремо ім'я автора з сесії замість форми
    author = session['username']
    user_id = session['user_id']

    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            image_path = save_image(file)
            print(f"Saved image path: {image_path}")

    try:
        success, message = user_db.insert_post(
            title=title,
            content=some_text,
            author=author,
            user_id=user_id,
            image_path=image_path
        )

        if success:
            flash('Пост успішно створено!', 'success')
            return redirect(url_for('all_blogs'))
        else:
            flash(message, 'error')
            return render_template('new_post.html')

    except Exception as e:
        flash(f'Помилка при створенні поста: {str(e)}', 'error')
        return render_template('new_post.html')


@app.route('/all_posts')
def my_posts():
    posts = user_db.select_all_posts()

    # Додаємо відладочний вивід
    for post in posts:
        print(f"Debug - Post data: {post}")
        print(f"Debug - Image path type: {type(post[5])}")

    formatted_posts = []
    for post in posts:
        post = list(post)
        # Перевіряємо тип даних перед викликом replace
        if post[5] is not None:
            # Конвертуємо в рядок, якщо це не рядок
            image_path = str(post[5]).replace('\\', '/')
            # Видаляємо 'uploads/' з початку шляху, якщо він там є
            if image_path.startswith('uploads/'):
                image_path = image_path[8:]
            post[5] = image_path
        formatted_posts.append(post)

    return render_template('all_posts.html', results=formatted_posts)


#@app.route('/my_posts')
def my_posts22():
    posts = user_db.select_all_posts()
    return render_template('all_posts.html', results=posts)

if __name__ == '__main__':

    app.run(debug=True)