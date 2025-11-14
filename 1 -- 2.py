import sqlite3

# Шаг 1 и 2: Установка соединения с БД
# Файл 'my_database.db' будет создан в текущей директории
conn = sqlite3.connect('my_database.db')

# Шаг 3: Создание курсора
cursor = conn.cursor()

# Шаг 4: Выполнение SQL-запроса на создание таблицы
create_table_query = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    age INTEGER
);
"""
cursor.execute(create_table_query)

# --- INSERT (Добавление данных) ---
# Вариант 1: По одному
insert_query = "INSERT INTO users (username, email, age) VALUES (?, ?, ?)"
user_data = ("alexey", 'alexey@example.com', 30)
cursor.execute(insert_query, user_data)

# Вариант 2: Несколько записей сразу
users_list = [
    ('maria', 'maria@example.com', 25),
    ('ivan', 'ivan@example.com', 35)
]
cursor.executemany(insert_query, users_list)

# --- SELECT (Чтение данных) ---
# Выбрать всех пользователей
cursor.execute("SELECT * FROM users")
all_users = cursor.fetchall() # Получить все строки
print("Все пользователи: - mogger.py:38")
for user in all_users:
    print(user)

# Выбрать с условием
cursor.execute("SELECT username, email FROM users WHERE age > 28")
adult_users = cursor.fetchall()
print("\nПользователи старше 28 лет: - mogger.py:45")
for user in adult_users:
    print(user)

# --- UPDATE (Обновление данных) ---
update_query = "UPDATE users SET email = ? WHERE username = ?"
new_data = ('new_email@example.com', 'alexey')
cursor.execute(update_query, new_data)
print("\nEmail пользователя alexey обновлен. - mogger.py:53")

# --- DELETE (Удаление данных) ---
delete_query = "DELETE FROM users WHERE username = ?"
cursor.execute(delete_query, ('ivan',))
print("Пользователь ivan удален. - mogger.py:58")

# Шаг 5: Сохранение изменений и закрытие соединения (ТОЛЬКО ПОСЛЕ ВСЕХ ОПЕРАЦИЙ)
conn.commit()
conn.close()
print("База данных и таблица успешно созданы! - mogger.py:63")
