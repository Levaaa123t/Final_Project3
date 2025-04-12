import sqlite3
from config import DB_NAME

# Предустановленные вопросы и ответы
default_questions = [
    ("Как оформить заказ?", "Для оформления заказа, пожалуйста, выберите интересующий вас товар и нажмите кнопку 'Добавить в корзину', затем перейдите в корзину и следуйте инструкциям для завершения покупки."),
    ("Как узнать статус моего заказа?", "Вы можете узнать статус вашего заказа, войдя в свой аккаунт на нашем сайте и перейдя в раздел 'Мои заказы'. Там будет указан текущий статус вашего заказа."),
    ("Как отменить заказ?", "Если вы хотите отменить заказ, пожалуйста, свяжитесь с нашей службой поддержки как можно скорее. Мы постараемся помочь вам с отменой заказа до его отправки."),
    ("Что делать, если товар пришел поврежденным?", "При получении поврежденного товара, пожалуйста, сразу свяжитесь с нашей службой поддержки и предоставьте фотографии повреждений. Мы поможем вам с обменом или возвратом товара."),
    ("Как связаться с вашей технической поддержкой?","Вы можете связаться с нашей технической поддержкой через телефон на нашем сайте или написать нам в чат-бота."),
    ("Как узнать информацию о доставке?","Информацию о доставке вы можете найти на странице оформления заказа на нашем сайте. Там указаны доступные способы доставки и сроки.")
]

class DB_questions:
    def __init__(self, database=DB_NAME):
        self.database = database
        self.create_tables()
        self.default_insert()

    def create_tables(self):
        """Создаёт таблицы, если их нет"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS questions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                question TEXT UNIQUE NOT NULL,
                                answer TEXT NOT NULL
                              )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS user_questions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                question TEXT NOT NULL,
                                status TEXT DEFAULT 'Ожидание' 
                              )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS admins( 
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           user_id INTEGER
                           )  ''')
            conn.commit()

    def __executemany(self, sql, data):
        """Массовая вставка данных"""
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()
    def __select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    def default_insert(self):
        """Добавляет предустановленные вопросы"""
        sql = 'INSERT OR IGNORE INTO questions (question, answer) VALUES (?, ?)'
        self.__executemany(sql, default_questions)

    def default_admins(self):
        sql = 'INSERT OR IGNORE INTO admins (user_id) VALUES (?)'
        data = [('ADMIN ID',)]
        self.__executemany(sql, data)

    # def get_answer(self, user_question):
    #     """Автоматически отвечает на часто задаваемые вопросы"""
    #     conn = sqlite3.connect(self.database)
    #     cursor = conn.cursor()
    #     words = user_question.split()
    #     if len(words) <2:
    #         return None
    #     conditions = [f"question LIKE ?" for _ in words]
    #     sql = "SELECT answer FROM questions WHERE " + " OR ".join(conditions)
    #     parameters = [f"%{word}%" for word in words]
    #     cursor.execute(sql, parameters)
    #     answer = cursor.fetchone()
    #     if answer:
    #         return answer[0]
    #     else:
    #         return None
    
    def get_answer(self, user_question):
        """Автоматически отвечает на часто задаваемые вопросы"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        
        # Разделяем вопрос на слова
        words = user_question.split()
        
        # Если слишком короткий запрос, то пропускаем
        if len(words) < 2:
            return None
        
        # Строим условия для поиска
        conditions = [f"question LIKE ?" for _ in words]
        sql = "SELECT answer FROM questions WHERE " + " OR ".join(conditions)
        parameters = [f"%{word}%" for word in words]
        
        cursor.execute(sql, parameters)
        answer = cursor.fetchone()
        if answer:
            return answer[0]
        else:
            return None
        # cursor.execute("SELECT answer FROM questions WHERE question = ?", (user_question,))
        # answer = cursor.fetchone()
        # return answer[0] if answer else None

    def save_user_question(self, user_id, question):
        """Сохраняет запрос пользователя к специалисту"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user_questions (user_id, question, status) VALUES (?, ?, 'Ожидание')", (user_id, question))
            conn.commit()

    def get_pending_questions(self):
        """Получает все вопросы пользователей, ожидающие ответа"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, question FROM user_questions WHERE status = 'Ожидание'")
        return cursor.fetchall()

    def update_question_status(self, question_id, status):
        """Обновляет статус вопроса пользователя"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE user_questions SET status = ? WHERE id = ?", (status, question_id))
            conn.commit()

    def clear_tables(self):
        """Очистить все данные в таблицах"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM questions") 
            cursor.execute("DELETE FROM user_questions")  
            conn.commit()

    def delete_user_question(self, question_id):
        """Удаляет решённый вопрос из базы данных"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_questions WHERE id = ? AND status = 'Решен'", (question_id,))
            conn.commit()
    def get_list_faq(self):
        sql = "SELECT question, answer FROM questions"
        return self.__select_data(sql)

    def check_id(self, user_id):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM admins WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_questions_pending(self):
        sql = 'SELECT id, question FROM user_questions'
        return self.__select_data(sql)
    
    def get_resolved_questions(self):
        sql = "SELECT id, question FROM user_questions WHERE status = 'Решен' "
        return self.__select_data(sql)
    
    def get_id(self, question_id):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_questions WHERE id = ?', (question_id,))
        result = cursor.fetchone()
        conn.close()
        return result
        

if __name__ == '__main__':
    manager = DB_questions(DB_NAME)
    manager.default_insert()
    #manager.default_admins()
    #manager.clear_tables()
    #manager.get_list_faq()