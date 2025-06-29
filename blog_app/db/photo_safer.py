import os
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Перевірка дозволених розширень файлів
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Функція для збереження файлу
def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Створюємо унікальне ім'я файлу
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        # Переконуємося, що папка існує
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        return os.path.join('uploads', unique_filename)
    return None