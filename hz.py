import psycopg2


connection = psycopg2.connect(
        database="maiid",
        user="postgres",
        password="12345",
        host="127.0.0.1",
        port="5432"
    )
cursor = connection.cursor()

id_s = 3
work_query = f'SELECT fio, role FROM faces WHERE id = %s'
cursor.execute(work_query, (id_s,))
connection.commit()
records = cursor.fetchall()
fio = bytes(records[0][0], 'cp1251').decode('cp866')
role = bytes(records[0][1], 'cp1251').decode('cp866')
print(fio)
print(role)