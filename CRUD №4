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
