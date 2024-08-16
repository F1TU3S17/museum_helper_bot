import bcrypt
from database import db, cur
def hash_password(password):
    # Генерация соли и хэширование пароля
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed

# Проверка пароля
def check_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

# Добавление нового администратора
# False, если новый админ не добавлен, иначе True
def add_admin(login, password):
    hashed_password = hash_password(password)
    is_reg = cur.execute("SELECT login FROM admins WHERE login == ?", (login,)).fetchone()
    if is_reg:
        return False
    else:
        cur.execute("INSERT INTO admins (login, password) VALUES (?, ?)", (login, hashed_password))
        db.commit()
        return True

# Проверка логина и пароля администратора
def authenticate_admin(login, password):
    cur.execute("SELECT password FROM admins WHERE login = ?", (login,))
    result = cur.fetchone()
    if result:
        stored_password = result[0]
        return check_password(stored_password, password)
    return False
