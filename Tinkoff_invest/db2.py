import sqlite3


database = sqlite3.connect('database')
cursor = database.cursor()
def user_exists(id):
    result =cursor.execute("SELECT * FROM `users` WHERE `id` = ?", (id, )).fetchall()
    return bool(len(result))

def add_user(message):
    cursor.execute("INSERT INTO users VALUES(?,?,?,?)", (message.chat.id, "1empty", "empty", "empty"))
    database.commit()
def add_user_nickname(message):
    cursor.execute("UPDATE users SET nickname=? WHERE id=?", (message.text, message.chat.id, ))
    database.commit()

def add_user_token(message):
    cursor.execute("UPDATE users SET token=? WHERE id=?", (message.text, message.chat.id, ))
    database.commit()

def add_user_email(message):
    cursor.execute("UPDATE users SET email=? WHERE id=?", (message.text, message.chat.id, ))
    database.commit()