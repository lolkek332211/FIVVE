import sqlite3
import csv
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime

class SimpleDatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("База данных блога")
        self.root.geometry("900x600")
        
        self.db_name = 'blog_database.db'
        self.connection = None
        self.cursor = None
        
        self.setup_database()
        self.create_interface()
        self.load_data()
    
    def setup_database(self):
        """Настройка базы данных"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            
            # Создание таблиц
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            self.connection.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")
    
    def create_interface(self):
        """Создание упрощенного интерфейса"""
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(top_frame, text="Обновить данные", 
                  command=self.load_data).pack(side='left', padx=5)
        ttk.Button(top_frame, text="Статистика", 
                  command=self.show_stats).pack(side='left', padx=5)
        ttk.Button(top_frame, text="Экспорт CSV", 
                  command=self.export_to_csv).pack(side='left', padx=5)
        ttk.Button(top_frame, text="Экспорт JSON", 
                  command=self.export_to_json).pack(side='left', padx=5)
        
        # Создание вкладок
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Вкладка пользователей
        users_frame = ttk.Frame(notebook, padding="10")
        notebook.add(users_frame, text="Пользователи")
        self.setup_users_tab(users_frame)
        
        # Вкладка постов
        posts_frame = ttk.Frame(notebook, padding="10")
        notebook.add(posts_frame, text="Посты")
        self.setup_posts_tab(posts_frame)
        
        # Вкладка операций
        operations_frame = ttk.Frame(notebook, padding="10")
        notebook.add(operations_frame, text="Операции")
        self.setup_operations_tab(operations_frame)
    
    def setup_users_tab(self, parent):
        """Настройка вкладки пользователей"""
        # Форма добавления пользователя
        form_frame = ttk.LabelFrame(parent, text="Добавить пользователя", padding="10")
        form_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(form_frame, text="Имя:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.email_entry = ttk.Entry(form_frame, width=30)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Добавить", 
                  command=self.add_user).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Очистить", 
                  command=self.clear_user_form).pack(side='left', padx=5)
        
        # Таблица пользователей
        table_frame = ttk.LabelFrame(parent, text="Список пользователей", padding="10")
        table_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Name', 'Email', 'Created')
        self.users_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        self.users_tree.heading('ID', text='ID')
        self.users_tree.heading('Name', text='Имя')
        self.users_tree.heading('Email', text='Email')
        self.users_tree.heading('Created', text='Дата создания')
        
        self.users_tree.column('ID', width=50)
        self.users_tree.column('Name', width=150)
        self.users_tree.column('Email', width=200)
        self.users_tree.column('Created', width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Кнопки управления таблицей
        control_frame = ttk.Frame(table_frame)
        control_frame.pack(fill='x', pady=5)
        
        ttk.Button(control_frame, text="Удалить выбранного", 
                  command=self.delete_user).pack(side='left', padx=5)
    
    def setup_posts_tab(self, parent):
        """Настройка вкладки постов"""
        # Форма добавления поста
        form_frame = ttk.LabelFrame(parent, text="Добавить пост", padding="10")
        form_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(form_frame, text="Заголовок:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.title_entry = ttk.Entry(form_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="ID автора:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.user_id_entry = ttk.Entry(form_frame, width=30)
        self.user_id_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Содержание:").grid(row=2, column=0, sticky='nw', padx=5, pady=5)
        self.content_text = scrolledtext.ScrolledText(form_frame, width=40, height=4)
        self.content_text.grid(row=2, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Добавить пост", 
                  command=self.add_post).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Очистить", 
                  command=self.clear_post_form).pack(side='left', padx=5)
        
        # Таблица постов
        table_frame = ttk.LabelFrame(parent, text="Список постов", padding="10")
        table_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Title', 'Author', 'Created')
        self.posts_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        self.posts_tree.heading('ID', text='ID')
        self.posts_tree.heading('Title', text='Заголовок')
        self.posts_tree.heading('Author', text='Автор')
        self.posts_tree.heading('Created', text='Дата создания')
        
        self.posts_tree.column('ID', width=50)
        self.posts_tree.column('Title', width=200)
        self.posts_tree.column('Author', width=150)
        self.posts_tree.column('Created', width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.posts_tree.yview)
        self.posts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.posts_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Кнопки управления таблицей
        control_frame = ttk.Frame(table_frame)
        control_frame.pack(fill='x', pady=5)
        
        ttk.Button(control_frame, text="Удалить выбранный", 
                  command=self.delete_post).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Показать содержание", 
                  command=self.show_post_content).pack(side='left', padx=5)
    
    def setup_operations_tab(self, parent):
        """Настройка вкладки операций"""
        # Импорт/Экспорт
        io_frame = ttk.LabelFrame(parent, text="Импорт/Экспорт", padding="10")
        io_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(io_frame, text="Импорт из CSV", 
                  command=self.import_from_csv).pack(fill='x', pady=2)
        ttk.Button(io_frame, text="Импорт из JSON", 
                  command=self.import_from_json).pack(fill='x', pady=2)
        
        # Поиск
        search_frame = ttk.LabelFrame(parent, text="Поиск", padding="10")
        search_frame.pack(fill='x', pady=(0, 10))
        
        search_row = ttk.Frame(search_frame)
        search_row.pack(fill='x', pady=5)
        
        ttk.Label(search_row, text="Поиск:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_row, width=20)
        self.search_entry.pack(side='left', padx=5)
        ttk.Button(search_row, text="Найти пользователей", 
                  command=self.search_users).pack(side='left', padx=5)
        
        # Лог операций
        log_frame = ttk.LabelFrame(parent, text="Лог операций", padding="10")
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15)
        self.log_text.pack(fill='both', expand=True)
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
    
    def load_data(self):
        """Загрузка данных в таблицы"""
        try:
            # Загрузка пользователей
            self.users_tree.delete(*self.users_tree.get_children())
            self.cursor.execute("SELECT * FROM users ORDER BY id")
            for user in self.cursor.fetchall():
                self.users_tree.insert('', 'end', values=user)
            
            # Загрузка постов
            self.posts_tree.delete(*self.posts_tree.get_children())
            self.cursor.execute('''
                SELECT p.id, p.title, u.name, p.created_at 
                FROM posts p 
                JOIN users u ON p.user_id = u.id 
                ORDER BY p.id
            ''')
            for post in self.cursor.fetchall():
                self.posts_tree.insert('', 'end', values=post)
            
            self.log_message("Данные загружены")
        except Exception as e:
            self.log_message(f"Ошибка загрузки: {e}")
    
    def add_user(self):
        """Добавление нового пользователя"""
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not name or not email:
            messagebox.showwarning("Предупреждение", "Заполните все поля")
            return
        
        try:
            self.cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)", 
                (name, email)
            )
            self.connection.commit()
            self.log_message(f"Добавлен пользователь: {name}")
            self.clear_user_form()
            self.load_data()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Пользователь с таким email уже существует")
    
    def delete_user(self):
        """Удаление выбранного пользователя"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления")
            return
        
        user_id = self.users_tree.item(selected[0])['values'][0]
        user_name = self.users_tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {user_name}?"):
            self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self.connection.commit()
            self.log_message(f"Удален пользователь: {user_name}")
            self.load_data()
    
    def add_post(self):
        """Добавление нового поста"""
        title = self.title_entry.get().strip()
        user_id = self.user_id_entry.get().strip()
        content = self.content_text.get('1.0', 'end').strip()
        
        if not title or not user_id or not content:
            messagebox.showwarning("Предупреждение", "Заполните все поля")
            return
        
        try:
            user_id = int(user_id)
        except ValueError:
            messagebox.showerror("Ошибка", "ID автора должен быть числом")
            return
        
        # Проверка существования пользователя
        self.cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not self.cursor.fetchone():
            messagebox.showerror("Ошибка", f"Пользователь с ID {user_id} не существует")
            return
        
        try:
            self.cursor.execute(
                "INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
                (title, content, user_id)
            )
            self.connection.commit()
            self.log_message(f"Добавлен пост: {title}")
            self.clear_post_form()
            self.load_data()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")
    
    def delete_post(self):
        """Удаление выбранного поста"""
        selected = self.posts_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пост для удаления")
            return
        
        post_id = self.posts_tree.item(selected[0])['values'][0]
        post_title = self.posts_tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Подтверждение", f"Удалить пост '{post_title}'?"):
            self.cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            self.connection.commit()
            self.log_message(f"Удален пост: {post_title}")
            self.load_data()
    
    def show_post_content(self):
        """Показать содержание выбранного поста"""
        selected = self.posts_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пост")
            return
        
        post_id = self.posts_tree.item(selected[0])['values'][0]
        
        self.cursor.execute("SELECT content FROM posts WHERE id = ?", (post_id,))
        content = self.cursor.fetchone()[0]
        
        content_window = tk.Toplevel(self.root)
        content_window.title("Содержание поста")
        content_window.geometry("500x300")
        
        text_widget = scrolledtext.ScrolledText(content_window, wrap='word')
        text_widget.insert('1.0', content)
        text_widget.config(state='disabled')
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
    
    def export_to_csv(self):
        """Экспорт пользователей в CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if filename:
            try:
                users = self.cursor.execute("SELECT * FROM users").fetchall()
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['ID', 'Name', 'Email', 'Created At'])
                    writer.writerows(users)
                
                self.log_message(f"Данные экспортированы в CSV: {filename}")
                messagebox.showinfo("Успех", "Данные успешно экспортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    def export_to_json(self):
        """Экспорт пользователей в JSON"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filename:
            try:
                users = self.cursor.execute("SELECT * FROM users").fetchall()
                columns = ['id', 'name', 'email', 'created_at']
                result = [dict(zip(columns, user)) for user in users]
                
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(result, file, indent=2, ensure_ascii=False)
                
                self.log_message(f"Данные экспортированы в JSON: {filename}")
                messagebox.showinfo("Успех", "Данные успешно экспортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    def import_from_csv(self):
        """Импорт пользователей из CSV"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader)  # Пропускаем заголовок
                    
                    imported = 0
                    for row in reader:
                        if len(row) >= 3:
                            try:
                                self.cursor.execute(
                                    "INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)",
                                    (row[1], row[2])
                                )
                                imported += 1
                            except:
                                continue
                
                self.connection.commit()
                self.log_message(f"Импортировано {imported} пользователей из CSV")
                self.load_data()
                messagebox.showinfo("Успех", f"Импортировано {imported} пользователей")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка импорта: {e}")
    
    def import_from_json(self):
        """Импорт пользователей из JSON"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    imported = 0
                    for item in data:
                        try:
                            self.cursor.execute(
                                "INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)",
                                (item['name'], item['email'])
                            )
                            imported += 1
                        except:
                            continue
                
                self.connection.commit()
                self.log_message(f"Импортировано {imported} пользователей из JSON")
                self.load_data()
                messagebox.showinfo("Успех", f"Импортировано {imported} пользователей")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка импорта: {e}")
    
    def show_stats(self):
        """Показать статистику"""
        self.cursor.execute('''
            SELECT u.name, COUNT(p.id) as post_count 
            FROM users u 
            LEFT JOIN posts p ON u.id = p.user_id 
            GROUP BY u.id 
            ORDER BY post_count DESC
        ''')
        stats = self.cursor.fetchall()
        
        stats_text = "Статистика пользователей:\n\n"
        for stat in stats:
            stats_text += f"{stat[0]}: {stat[1]} постов\n"
        
        messagebox.showinfo("Статистика", stats_text)
        self.log_message("Показана статистика пользователей")
    
    def search_users(self):
        """Поиск пользователей"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Предупреждение", "Введите поисковый запрос")
            return
        
        self.cursor.execute(
            "SELECT * FROM users WHERE name LIKE ? OR email LIKE ?", 
            (f'%{keyword}%', f'%{keyword}%')
        )
        results = self.cursor.fetchall()
        
        if results:
            result_text = f"Найдено пользователей: {len(results)}\n\n"
            for user in results:
                result_text += f"ID: {user[0]}\nИмя: {user[1]}\nEmail: {user[2]}\n\n"
            messagebox.showinfo("Результаты поиска", result_text)
        else:
            messagebox.showinfo("Результаты поиска", "Пользователи не найдены")
        
        self.log_message(f"Выполнен поиск: '{keyword}'")
    
    def clear_user_form(self):
        """Очистка формы пользователя"""
        self.name_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
    
    def clear_post_form(self):
        """Очистка формы поста"""
        self.title_entry.delete(0, 'end')
        self.user_id_entry.delete(0, 'end')
        self.content_text.delete('1.0', 'end')
    
    def __del__(self):
        """Закрытие соединения с БД при удалении объекта"""
        if self.connection:
            self.connection.close()

def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = SimpleDatabaseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
