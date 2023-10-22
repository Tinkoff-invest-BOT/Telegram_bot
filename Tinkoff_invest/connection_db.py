import pymysql
from passwords import *

try:
    connect = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor

    )
except Exception as e:
    print("Что то пошло не так ...")
    print(e)
