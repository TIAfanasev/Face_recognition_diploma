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

qss = 'QPushButton {background-color: #0095DA;' \
              'border-style: outset;'\
              'border-width: 2px;'\
              'border-radius: 6px;'\
              'border-color: #FFFFFF;'\
              'font: bold 30px;'\
              'min-width: 10em;'\
              'padding: 6px;'\
              'color: #FFFFFF;' \
              'margin: 18px;' \
              'text-align:left}'