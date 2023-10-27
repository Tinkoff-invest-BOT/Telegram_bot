import logging
from aiogram import Bot, Dispatcher, executor, types
import markups as nav
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

class Database:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def add_user(self, user_id):
        self.connection.ping()
        with self.connection as cur:
            tmp = f"INSERT INTO people (user_id) VALUES ({user_id});"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def user_exists(self, user_id):
        self.connection.ping()
        with self.connection:
            tmp = f"SELECT * FROM people WHERE user_id ={user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchall()
            return bool((len(result)))

    def set_nickname(self, user_id, nickname):
        self.connection.ping()
        with self.connection:
            tmp = f"UPDATE people SET nickname = {repr(nickname)} WHERE `user_id`= {user_id};"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def set_email(self, user_id, email):
        self.connection.ping()
        with self.connection:
            tmp = f"UPDATE `people` SET `email` = {repr(email)} WHERE `user_id`= {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def set_tocken(self, user_id, token):
        self.connection.ping()
        with self.connection:
            tmp = f"UPDATE `people` SET `token` = {repr(token)} WHERE `user_id`= {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def get_signup(self, user_id):
        self.connection.ping()
        with self.connection:
            tmp = f"SELECT `sign_up` FROM `people` WHERE `user_id` = {user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchall()
            for row in result:
                sign_up = row['sign_up']
            return sign_up

    def set_sign_up(self, user_id, sign_up):
        self.connection.ping()
        with self.connection:
            tmp = f"UPDATE `people` SET `sign_up` = {repr(sign_up)} WHERE `user_id`= {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def set_status(self, user_id, status):
        self.connection.ping()
        with self.connection:
            tmp = f"UPDATE `people` SET `status` = {repr(status)} WHERE `user_id`= {user_id}"
            result = self.cursor.execute(tmp)
            self.connection.commit()
            return result

    def get_status(self, user_id):
        self.connection.ping()
        with self.connection:
            tmp = f"SELECT `status` FROM `people` WHERE `user_id` = {user_id}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchall()
            for row in result:
                sign_up = row['status']
            return sign_up


    def get_figi(self, figi):
        self.connection.ping()
        with self.connection:
            tmp = f"SELECT `name` FROM `shares` WHERE `share` = {repr(figi)}"
            self.cursor.execute(tmp)
            result = self.cursor.fetchall()
            for row in result:
                fg = row['name']
            return fg

    # def get_token(self, user_id):
    #     self.connection.ping()
    #     with self.connection:
    #         tmp = f"SELECT `token` FROM `people` WHERE `user_id` = {user_id}"
    #         self.cursor.execute(tmp)
    #         result = self.cursor.fetchall()
    #         if result == []:
    #             return 'none'
    #         else:
    #             for row in result:
    #                 ravil = row['token']
    #                 return ravil
