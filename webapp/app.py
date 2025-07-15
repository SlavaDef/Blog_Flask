import os

from flask import render_template, Flask, request, session, flash, redirect, url_for

from blog_app.db.photo_safer import save_image
from blog_app.db.service import UserDatabase
import html

from blog_app.decorator import check_post_owner

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Обмеження розміру файлу (16MB)
app.secret_key = os.urandom(24) # без ключа сесії не працюють


user_db = UserDatabase()
#user_db.check_table_structure()

@app.route('/')
def main_page():
    return redirect(url_for('my_posts'))



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
        return redirect(url_for('register')) # переадресація на метод def register()
    return render_template('profile.html') # повернення сторінки


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
            return redirect(url_for('my_posts'))
        else:
            flash(message, 'error')
            return render_template('new_post.html')

    except Exception as e:
        flash(f'Помилка при створенні поста: {str(e)}', 'error')
        return render_template('all_posts.html')


@app.route('/all_posts')
def my_posts():
    posts = user_db.select_all_posts()
    return render_template('all_posts.html', results=posts)


@app.route('/all_my_posts')
@check_post_owner
def all_my_posts():

    author = session['username']
    posts = user_db.get_posts_by_author(author=author)

    if not posts:
        flash('У вас поки немає постів', 'info')

    return render_template('all_posts.html', results=posts)


@app.route('/post/<int:post_id>')
#@check_post_owner
def post_detail(post_id):
    post = user_db.get_post(post_id)
    if post is None:
        return "Пост не найден", 404
    return render_template('post_detail.html', post=post)



@app.route('/delete/<int:post_id>', methods = ['POST'])
@check_post_owner
def delete_post_route(post_id):
    try:
        user_db.delete_post(post_id)
        flash('Пост успішно видалено', 'success')
    except Exception as e:
        flash(f'Помилка при видаленні поста: {str(e)}', 'error')

    return redirect(url_for('my_posts'))


@app.route('/update/<int:post_id>', methods=['GET', 'POST'])
@check_post_owner
def update_post_route(post_id):
    if request.method == 'POST':

        try:
            title = request.form.get('title')
            some_text = request.form.get('some_text')
            #author = request.form.get('author')  # отримуємо значення з форми

            # Обробка зображення
            image_path = None
            if 'image' in request.files and request.files['image'].filename != '':
                # Якщо нове фото не завантажене, передаємо None,
                # і функція update_post збереже існуюче

                file = request.files['image']
                image_path = save_image(file)

            # Викликаємо update_post з правильним порядком аргументів
            success = user_db.update_post(
                post_id=post_id,
                title=title,
                content=some_text,
                #author=author,  # переконайтесь що це значення не None
                image_path=image_path
            )

            if success:
                flash('Пост успішно відредаговано', 'success')
            return redirect(url_for('my_posts'))

        except Exception as e:
            flash(f'Помилка при редагуванні поста: {str(e)}', 'error')
            return redirect(url_for('my_posts'))


if __name__ == '__main__':

    app.run(debug=True)