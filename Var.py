import psycopg2
from PyQt5.QtGui import QFont

connection = psycopg2.connect(
        database="maiid",
        user="postgres",
        password="12345",
        host="127.0.0.1",
        port="5432"
    )
cursor = connection.cursor()

roles = ['Преподаватель', 'М3О-416Б-19', 'М3О-417Бк-19', 'М3О-418Бк-19', 'Слушатель', 'Роль не выбрана']
roles = sorted(roles)

font = QFont()
font.setFamily('MS Shell Dlg 2')
font.setPointSize(10)
