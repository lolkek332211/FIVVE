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
