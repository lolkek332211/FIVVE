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
