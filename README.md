Общий подход:
Мы будем использовать язык Python и встроенный модуль sqlite3 для взаимодействия с СУБД SQLite. Это идеально подходит для обучения и небольших проектов.

1. Создание и настройка баз данных в СУБД SQLite
Цель: Создать файл базы данных, подключиться к нему и создать таблицы с определенной структурой.

План действий:

Импортировать модуль sqlite3.

Установить соединение с базой данных (файл будет создан автоматически).

Создать объект cursor для выполнения SQL-запросов.

Выполнить SQL-запрос CREATE TABLE для определения структуры таблицы.

Зафиксировать изменения (commit) и закрыть соединение.

Пример кода:

python
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

# Шаг 5: Сохранение изменений и закрытие соединения
conn.commit()
conn.close()
print("База данных и таблица успешно созданы!")
2. Выполнение SQL-запросов для манипуляции данными
Цель: Научиться вставлять, выбирать, обновлять и удалять данные с помощью SQL.

Основные операторы:

INSERT - добавление новых записей.

SELECT - выборка данных (чтение).

UPDATE - обновление существующих записей.

DELETE - удаление записей.

Пример кода (продолжение):

python
# ... (после создания таблицы)

# --- INSERT (Добавление данных) ---
# Вариант 1: По одному
insert_query = "INSERT INTO users (username, email, age) VALUES (?, ?, ?)"
user_data = ('alexey', 'alexey@example.com', 30)
cursor.execute(insert_query, user_data)

# Вариант 2: Несколько записей сразу
users_list = [
    ('maria', 'maria@example.com', 25),
    ('ivan', 'ivan@example.com', 35)
]
cursor.executemany(insert_query, users_list)
conn.commit()

# --- SELECT (Чтение данных) ---
# Выбрать всех пользователей
cursor.execute("SELECT * FROM users")
all_users = cursor.fetchall() # Получить все строки
print("Все пользователи:")
for user in all_users:
    print(user)

# Выбрать с условием
cursor.execute("SELECT username, email FROM users WHERE age > 28")
adult_users = cursor.fetchall()
print("\nПользователи старше 28 лет:")
for user in adult_users:
    print(user)

# --- UPDATE (Обновление данных) ---
update_query = "UPDATE users SET email = ? WHERE username = ?"
new_data = ('new_email@example.com', 'alexey')
cursor.execute(update_query, new_data)
conn.commit()
print("\nEmail пользователя alexey обновлен.")

# --- DELETE (Удаление данных) ---
delete_query = "DELETE FROM users WHERE username = ?"
cursor.execute(delete_query, ('ivan',))
conn.commit()
print("Пользователь ivan удален.")
3. Организация работы с файлами данных (CSV, JSON)
Цель: Импортировать данные из внешних файлов в базу данных и экспортировать их обратно.

Работа с CSV
Пример кода (Импорт CSV в БД):

Предположим, у нас есть файл users.csv:

csv
username,email,age
petr,petr@example.com,40
svetlana,svetlana@example.com,28
python
import csv
import sqlite3

conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

with open('users.csv', 'r', newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        cursor.execute(
            "INSERT INTO users (username, email, age) VALUES (?, ?, ?)",
            (row['username'], row['email'], int(row['age']))
        )

conn.commit()
conn.close()
print("Данные из CSV импортированы в БД.")
Работа с JSON
Пример кода (Экспорт данных из БД в JSON):

python
import json
import sqlite3

conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
columns = [column[0] for column in cursor.description] # Получаем названия колонок
result = []

for row in cursor.fetchall():
    # Создаем словарь для каждой строки, связывая колонки со значениями
    result.append(dict(zip(columns, row)))

with open('users_export.json', 'w', encoding='utf-8') as jsonfile:
    json.dump(result, jsonfile, ensure_ascii=False, indent=4)

conn.close()
print("Данные из БД экспортированы в JSON.")
4. Реализация операций CRUD (Create, Read, Update, Delete)
Цель: Создать функции-обертки для каждой CRUD-операции. Это основа для построения приложений.

Пример кода (Класс для работы с БД):

python
import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        """Открывает соединение при входе в контекстный менеджер."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрывает соединение при выходе из контекстного менеджера."""
        self.conn.close()

    # CREATE
    def create_user(self, username, email, age):
        query = "INSERT INTO users (username, email, age) VALUES (?, ?, ?)"
        self.cursor.execute(query, (username, email, age))
        self.conn.commit()
        print(f"Пользователь {username} создан.")

    # READ
    def read_all_users(self):
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()

    def read_user_by_username(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone() # Возвращает одну запись или None

    # UPDATE
    def update_user_email(self, username, new_email):
        query = "UPDATE users SET email = ? WHERE username = ?"
        self.cursor.execute(query, (new_email, username))
        self.conn.commit()
        print(f"Email пользователя {username} обновлен.")

    # DELETE
    def delete_user(self, username):
        query = "DELETE FROM users WHERE username = ?"
        self.cursor.execute(query, (username,))
        self.conn.commit()
        print(f"Пользователь {username} удален.")

# Использование класса
with DatabaseManager('my_database.db') as db:
    # Create
    db.create_user("olga", "olga@example.com", 29)

    # Read
    all_users = db.read_all_users()
    print("Все пользователи:", all_users)

    user = db.read_user_by_username("olga")
    print("Найден пользователь:", user)

    # Update
    db.update_user_email("olga", "olga_new@example.com")

    # Delete
    db.delete_user("maria")
Итоговый совет:
Начните с основ: Выполняйте шаги последовательно. Сначала создайте базу и таблицу.

Экспериментируйте с SQL: Попробуйте разные SELECT-запросы с WHERE, ORDER BY, JOIN (если создадите несколько связанных таблиц).

Обработка ошибок: В реальном коде добавляйте try...except блоки для обработки ошибок (например, попытка добавить пользователя с неуникальным именем).

Безопасность: Всегда используйте параметризованные запросы (как в примерах с ?), чтобы избежать SQL-инъекций.

Этот план даст вам прочную практическую основу для проектирования и администрирования баз данных с использованием SQLite и Python. Удачи в изучении!

