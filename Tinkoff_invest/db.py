import sqlite3
# import os.path
# Base_dir = os.path.dirname(os.path.abspath('database.db'))

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool((len(result)))

    def set_nickname(self, user_id, nickname):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `nickname` = ? WHERE `user_id`= ?", (nickname, user_id,))

    def set_email(self, user_id, email):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `email` = ? WHERE `user_id`= ?", (email, user_id, ))

    def set_tocken(self, user_id, token):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `token` = ? WHERE `user_id`= ?", (token, user_id, ))

    def get_signup(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `sign_up` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                sign_up = str(row[0])
            return sign_up

    def set_sign_up(self, user_id, sign_up):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `sign_up` = ? WHERE `user_id`= ?", (sign_up, user_id,))