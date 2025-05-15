import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="teleg_bot_base.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self.update_table_structure()

    def _create_tables(self):
        """Создаёт необходимые таблицы, если они ещё не существуют."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                username TEXT,
                date TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS selected_dates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                name TEXT,
                description TEXT,
                time TEXT
            )
        ''')
        self.conn.commit()

    def add_user(self, user_id: int, username: str):
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        username = username.strip().lower()  # Убираем лишние пробелы и приводим к нижнему регистру

        # Проверяем, есть ли пользователь в базе данных
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = self.cursor.fetchone()  # Извлекаем пользователя

        if user is None:
            # Если пользователь не найден, добавляем его
            self.cursor.execute(
                'INSERT INTO users (user_id, username, date) VALUES (?, ?, ?)',
                (user_id, username, current_date)
            )
            self.conn.commit()
            return "Новый пользователь добавлен в базу данных."
        else:
            # Если пользователь найден, проверяем, нужно ли обновить имя
            if user[2] != username:
                self.cursor.execute(
                    'UPDATE users SET username = ? WHERE user_id = ?',
                    (username, user_id)
                )
                self.conn.commit()
                return "Имя пользователя обновлено."
            return "Пользователь уже существует в базе данных."

    def get_events_by_month(self, year: int, month: int):
        """Получает все события за указанный месяц."""
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{32}"  # Для получения последнего дня месяца
        self.cursor.execute(
            "SELECT date, time, name FROM selected_dates WHERE date BETWEEN ? AND ?",
            (start_date, end_date)
        )
        events = self.cursor.fetchall()
        return [{"date": row[0], "time": row[1], "name": row[2]} for row in events]

    def save_event(self, user_id: int, date: str, name: str, description: str, time: str):
        """Сохраняет событие в базу данных."""
        self.cursor.execute('''
            INSERT INTO selected_dates (user_id, date, name, description, time)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, date, name, description, time))
        self.conn.commit()
        return "Событие успешно сохранено."


    def update_table_structure(self):
        """Обновляет структуру таблицы selected_dates."""
        existing_columns = {row[1] for row in self.cursor.execute("PRAGMA table_info(selected_dates)")}
        columns_to_add = {
            "name": "TEXT",
            "description": "TEXT",
            "time": "TEXT"
        }

        for column, column_type in columns_to_add.items():
            if column not in existing_columns:
                self.cursor.execute(f"ALTER TABLE selected_dates ADD COLUMN {column} {column_type}")
        self.conn.commit()

    def get_user_by_username(self, username: str):
        """Метод для получения пользователя по имени пользователя"""
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = self.cursor.fetchone()  # Получаем одного пользователя
        return user

    def delete_event(self, user_id: int, date: str, time: str):
        """Удаляет событие из базы данных по дате и времени."""
        self.cursor.execute(
            "DELETE FROM selected_dates WHERE user_id = ? AND date = ? AND time = ?",
            (user_id, date, time)
        )
        self.conn.commit()
        return "Событие успешно удалено."

    def save_date(self, user_id: int, date: str):
        """Сохраняет дату для пользователя."""
        self.cursor.execute('''
            INSERT INTO selected_dates (user_id, date)
            VALUES (?, ?)
        ''', (user_id, date))
        self.conn.commit()
        return "Дата успешно сохранена."

    def get_user_events(self, user_id: int):
        """Возвращает список всех событий для указанного пользователя."""
        self.cursor.execute('''
               SELECT date, name, description, time
               FROM selected_dates
               WHERE user_id = ?
               ORDER BY date, time
           ''', (user_id,))
        rows = self.cursor.fetchall()

        # Преобразуем данные в удобный формат (список словарей)
        events = [
            {"date": row[0], "name": row[1], "description": row[2], "time": row[3]}
            for row in rows
        ]
        return events

    def get_events_by_date(self, date: str):
        """
        Возвращает события для конкретной даты.
        :param date: Дата в формате 'YYYY-MM-DD'
        :return: Список событий
        """
        query = "SELECT time, name, description FROM events WHERE date = ?"
        return self.execute_query(query, (date,))

    def execute_query(self, query: str, params: tuple = ()):
        """
        Выполняет запрос к базе данных.
        :param query: SQL-запрос.
        :param params: Параметры для SQL-запроса.
        :return: Результаты запроса.
        """
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.fetchall()  # Возвращает результаты запроса
        except sqlite3.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []

    def get_last_event(self):
        self.cursor.execute('SELECT * FROM selected_dates ORDER BY id DESC LIMIT 1')
        row = self.cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "date": row[2],
                "name": row[3],
                "description": row[4],
                "time": row[5]
            }
        return None

    def close(self):
        """Закрывает соединение с базой данных."""
        self.conn.close()
