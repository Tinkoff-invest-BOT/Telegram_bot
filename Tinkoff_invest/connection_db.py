import psycopg2

try:
    connection = psycopg2.connect(
        dbname="mydatabase",
        user="admin",
        password="root",
        host="localhost",
        port="5432"
    )

except Exception as e:
    print("Ошибочка(( проверь  правильность данных для подключения к бд")
    print(e)
