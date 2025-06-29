import os

from flask import render_template, Flask, request, session, flash, redirect, url_for
from blog_app.db.user_service import UserDatabase

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Обмеження розміру файлу (16MB)
app.secret_key = os.urandom(24) # без ключа сесії не працюють


user_db = UserDatabase()

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



if __name__ == '__main__':

    app.run(debug=True)