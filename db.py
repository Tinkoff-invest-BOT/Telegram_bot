import logging
from aiogram import Bot, Dispatcher, executor, types
import markups as nav
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from psycopg2.extras import DictCursor
from connection_db import connection

class Database:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor(cursor_factory=DictCursor)

    def add_user(self, user_id):
        self.cursor.execute("SELECT 1")
        with self.connection as cur:
            tmp = f"INSERT INTO users (user_id) VALUES ({user_id});"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def user_exists(self, user_id):
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT * FROM users WHERE user_id = {user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchall()
            return bool((len(result)))

    def set_nickname(self, user_id, nickname):
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"UPDATE users SET nickname = {repr(nickname)} WHERE user_id= {user_id};"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def set_email(self, user_id, email):
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"UPDATE users SET email = {repr(email)} WHERE user_id = {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def set_tocken(self, user_id, token):
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"UPDATE users SET token = {repr(token)} WHERE user_id= {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def get_signup(self, user_id):
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT sign_up FROM users WHERE user_id = {user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchall()
            for row in result:
                sign_up = row['sign_up']
            return sign_up

    def set_sign_up(self, user_id, sign_up):
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"UPDATE users SET sign_up = {repr(sign_up)} WHERE user_id= {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def set_status(self, user_id, status):
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"UPDATE users SET status = {repr(status)} WHERE user_id= {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def set_token_status(self, user_id, status):
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"UPDATE users SET token_status = {repr(status)} WHERE user_id = {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def get_status(self, user_id):
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT status FROM users WHERE user_id = {user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchall()
            for row in result:
                sign_up = row['status']
            return sign_up


    def get_figi(self, figi):
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
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT token_status FROM users WHERE user_id = {user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchone()
            return result


    def set_share(self, user_id, shares_list):
        # shares_str = ",".join(f"'{share}'" for share in shares_list)  # костыль - НЕ ТРОГАТЬ
        query = f"UPDATE users SET shares_to_public = ARRAY{shares_list} WHERE user_id = {user_id}"
        self.cursor.execute(query)
        self.connection.commit()
        
        
    def get_share(self, user_id):
        query = f"SELECT shares_to_public FROM users WHERE user_id = {user_id}"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result and result['shares_to_public'] is not None:
            return result['shares_to_public']
        return []
    
    
    def get_token(self, user_id):
        self.cursor.execute(f"SELECT token FROM users WHERE user_id = {user_id}")
        result = self.cursor.fetchone()
        return result['token'] if result else None
    
    
    def get_all_users(self):
        self.cursor.execute("SELECT user_id FROM users")
        return [row['user_id'] for row in self.cursor.fetchall()]
    

    def ticker_to_figi(self, ticker):
        self.cursor.execute(f"SELECT figi FROM tiki WHERE ticker = {repr(ticker)}")
        result = self.cursor.fetchone()
        return result[0]


    def ticker_to_name(self, ticker):
        self.cursor.execute(f"SELECT name FROM tiki WHERE ticker = {repr(ticker)}")
        result = self.cursor.fetchone()
        return result


    def share_exist(self, share):
        self.cursor.execute("SELECT 1")
        with self.connection:
            tmp = f"SELECT figi FROM tiki WHERE ticker = {repr(share)}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchone()
            if result:
                return True
            return False
        
        
    def get_all_tinkoff_tickers(self): 
        self.cursor.execute("SELECT ticker FROM tiki") 
        return [row['ticker'] for row in self.cursor.fetchall()]

    def get_all_tinkoff(self, fig):
        self.cursor.execute(f"SELECT * FROM tiki WHERE figi = {repr(fig)}")

        return [row for row in self.cursor.fetchall()]

    def get_ticker_parser(self, ticker):
        self.cursor.execute(f"SELECT parser FROM ticker_parser WHERE ticker = {repr(ticker)}")
        result = self.cursor.fetchone()
        if result:
            return result
        return False

    def set_share_to_parser(self, ticker):
        result = self.cursor.execute(f"INSERT INTO ticker_parser (ticker) VALUES ({repr(ticker)})")
        self.connection.commit()
        return result
    def set_parser_to_share(self, ticker, parser):
        result = self.cursor.execute(f"UPDATE ticker_parser SET parser = {repr(parser)} WHERE ticker = {repr(ticker)}")
        self.connection.commit()
        # result = self.cursor.execute(f"INSERT INTO ticker_parser (parser) VALUES ({repr(parser)})")

    # def get_shares_parser(self, share):
    #     self.cursor.execute(f"SELECT ticker FROM ")




