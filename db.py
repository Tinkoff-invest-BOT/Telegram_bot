import logging
from aiogram import Bot, Dispatcher, executor, types
import markups as nav
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from psycopg2.extras import DictCursor
from connection_db import connection
import json
from connection_db import connection


class Database:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor(cursor_factory=DictCursor)

    def add_user(self, user_id):
        '''
        Данная функция добавлет пользователя в базу данных
        '''
        self.cursor.execute("SELECT 1")
        with self.connection as cur:
            tmp = f"INSERT INTO users (user_id) VALUES ({user_id});"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def user_exists(self, user_id):
        '''
        Данная функция проверяет, существует ли пользователь с ,
        заданным user_id базе данных
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT * FROM users WHERE user_id = {user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchall()
            return bool((len(result)))

    def set_nickname(self, user_id, nickname):
        '''
        Данная функция по заданному user_id присваивает
        никнейм в базе данных
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"UPDATE users SET nickname = {repr(nickname)} WHERE user_id= {user_id};"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def set_email(self, user_id, email):
        '''
        Данная функция по заданному user_id присваивает
        email в базе данных
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"UPDATE users SET email = {repr(email)} WHERE user_id = {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def set_tocken(self, user_id, token):
        '''
        Данная функция по заданному user_id присваивает
        token в базе данных
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"UPDATE users SET token = {repr(token)} WHERE user_id= {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def get_signup(self, user_id):
        '''
        Данная функция проверяет информацию о том, 
        зарегестрирован пользователь или нет
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT sign_up FROM users WHERE user_id = {user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchall()
            for row in result:
                sign_up = row['sign_up']
            return sign_up

    def set_sign_up(self, user_id, sign_up):
        '''
        Данная функция устанавливает статус регистрации
        по заданному user_id
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"UPDATE users SET sign_up = {repr(sign_up)} WHERE user_id= {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def set_status(self, user_id, status):
        '''
        Данная функция устанавливает статус пользователя
        по заданному user_id
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"UPDATE users SET status = {repr(status)} WHERE user_id= {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def set_token_status(self, user_id, status):
        '''
        Данная функция устанавливает статус токена
        по заданному user_id
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"UPDATE users SET token_status = {repr(status)} WHERE user_id = {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def get_status(self, user_id):
        '''
        Данная функция выводит статус пользователя 
        по заданному user_id
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT status FROM users WHERE user_id = {user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchall()
            for row in result:
                sign_up = row['status']
            return sign_up


    def get_figi(self, figi):
        '''
        Данная функция получает название ценной бумаги
        по ее 'figi'
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT name FROM figi_2_comp WHERE figi = '{figi}'"
            self.cursor.execute(tmp)
            result = self.cursor.fetchall()
            if result:
                for row in result:
                    fg = row['name']
                return fg
            else:
                return 0
    def get_token_status(self, user_id):
        '''
        Данная функция проверяет наличие токена
        у пользователя
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT token_status FROM users WHERE user_id = {user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchone()
            return result


    def set_share(self, user_id, shares_list):
        '''
        Данная функция устанавливает список акций
        для пользователя в базу данных
        '''
        # shares_str = ",".join(f"'{share}'" for share in shares_list)  # костыль - НЕ ТРОГАТЬ
        query = f"UPDATE users SET shares_to_public = ARRAY{shares_list} WHERE user_id = {user_id}"
        self.cursor.execute(query)
        self.connection.commit()
        
        
    def get_share(self, user_id):
        '''
        Данная функция выводит список 
        выбранных акций пользователя
        '''
        query = f"SELECT shares_to_public FROM users WHERE user_id = {user_id}"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result and result['shares_to_public'] is not None:
            return result['shares_to_public']
        return []
    
    
    def get_token(self, user_id):
        '''
        Данная функция выводит токен пользователя
        '''
        self.cursor.execute(f"SELECT token FROM users WHERE user_id = {user_id}")
        result = self.cursor.fetchone()
        return result['token'] if result else None
    
    
    def get_all_users(self):
        '''
        Данная функция выводит список всех пользователей
        '''
        self.cursor.execute("SELECT user_id FROM users")
        return [row['user_id'] for row in self.cursor.fetchall()]
    

    def ticker_to_figi(self, ticker):
        '''
        Данная функция получает 'figi' по тикеру акции
        '''
        self.cursor.execute(f"SELECT figi FROM tiki WHERE ticker = {repr(ticker)}")
        result = self.cursor.fetchone()
        return result[0]


    def ticker_to_name(self, ticker):
        '''
        Данная функция получает название акции по 'figi'
        '''
        self.cursor.execute(f"SELECT name FROM tiki WHERE ticker = {repr(ticker)}")
        result = self.cursor.fetchone()
        return result


    def share_exist(self, share):
        '''
        Данная функция существет ли акция
        по заданному тикеру
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT figi FROM tiki WHERE ticker = {repr(share)}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchone()
            if result:
                return True
            return False

    def get_ticker_parser(self, ticker):
        '''
        Данная функция получает ифнормацию о парсере
        заданного тикера
        '''
        self.cursor.execute(f"SELECT parser FROM ticker_parser WHERE ticker = {repr(ticker)}")
        result = self.cursor.fetchone()
        if result:
            return result
        return False

    def set_share_to_parser(self, ticker):
        '''
        Данная функция устанавливает тикер в таблицу 
        для парсера (чтобы понимать откуда мы берем инфу по бумаге)
        '''
        result = self.cursor.execute(f"INSERT INTO ticker_parser (ticker) VALUES ({repr(ticker)})")
        self.connection.commit()
        return result
    
    def set_parser_to_share(self, ticker, parser):
        '''
        Данная функция 
        '''
        result = self.cursor.execute(f"UPDATE ticker_parser SET parser = {repr(parser)} WHERE ticker = {repr(ticker)}")
        self.connection.commit()
        # result = self.cursor.execute(f"INSERT INTO ticker_parser (parser) VALUES ({repr(parser)})")

    # def get_shares_parser(self, share):
    #     self.cursor.execute(f"SELECT ticker FROM ")

    def delete_user(self, user_id):
        query = f'DELETE FROM users WHERE user_id ={user_id}'
        self.cursor.execute(query)
        self.connection.commit()

    def set_levels(self, user_id, data):
        '''
        Добавляет информацию по отслеживанию стоимости бумаги пользователя
        '''
        ticker, operation, cost = data

        self.cursor.execute("SELECT shares_level FROM users WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()

        if result and result[0]:
            current_data = result[0]
        else:
            current_data = {}

        if ticker in current_data:
            current_data[ticker][operation] = int(cost)
        else:
            current_data[ticker] = {operation: int(cost)}

        updated_json_data = json.dumps(current_data)

        self.cursor.execute("UPDATE users SET shares_level = %s WHERE user_id = %s", (updated_json_data, user_id))
        self.connection.commit()


    def get_levels(self, user_id):
        '''
        Возвращает информацию по отслеживанию стоимости ценных бумаг пользователя
        '''
        self.cursor.execute("SELECT shares_level FROM users WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()[0]
        return result




    def delete_level(self, user_id, ticker):
        '''
        После отработки триггера удаляет информацию по отслеживанию бумаги
        '''
    
        self.cursor.execute("SELECT shares_level FROM users WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()

        if result and result[0]:
            current_data = result[0]

        if ticker in current_data:
            del current_data[ticker] 
            updated_json_data = json.dumps(current_data)

            self.cursor.execute("UPDATE users SET shares_level = %s WHERE user_id = %s", (updated_json_data, user_id))
            self.connection.commit()
            print(f"Информация по {ticker} успешно удалена.")
            
        
    def get_nickname(self, user_id):
        '''
        Возвращает nickname по user_id
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT nickname FROM users WHERE user_id = {user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchone()
            return result['nickname']
        
        
    def get_email(self, user_id):
        '''
        Возвращает email по user_id
        '''
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT email FROM users WHERE user_id = {user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchone()
            return result['email']
            
db = Database(connection)
