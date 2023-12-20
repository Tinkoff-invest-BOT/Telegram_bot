import psycopg2

try:
    connection = psycopg2.connect(
        dbname="railway",
        user="postgres",
        password="F*FfEeGdBb42dF1aF-*e6bGff-cFGg3a",
        host="roundhouse.proxy.rlwy.net",
        port="19279"
    )

except Exception as e:
    print("Ошибочка(( проверь  правильность данных для подключения к бд")
    print(e)
