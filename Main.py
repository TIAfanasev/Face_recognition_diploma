from PyQt5 import Qt, QtWidgets
from PyQt5.QtCore import Qt as Qtt, QTimer
from PyQt5.QtGui import QFont
import sys
import GroupSelection
import UserProfile
import AllUsers
import biometric
import make_cascade
import ident
import psycopg2
import shutil
from threading import Thread
import CheckStudents
import multiprocessing


def make_new():
    ec = UserProfile.FaceWindow()
    ec.exec_()


def whois():
    user = ident.__init__()
    if user == -1:
        print(f'Распознан неизвестный человек')
        return [0, 0]
    elif user != -2:
        work_query = f'SELECT fio, role FROM faces WHERE id = %s'
        cursor.execute(work_query, (user,))
        connection.commit()
        records = cursor.fetchall()
        fio = bytes(records[0][0], 'cp1251').decode('cp866')
        role = bytes(records[0][1], 'cp1251').decode('cp866')
        print(f'Распознан {fio} ({role})')
        return [fio, role]


def go_to_list():
    lw = AllUsers.AllUsersWindow()
    lw.exec_()


class MainWindow(Qt.QWidget):

    def __init__(self):
        super().__init__()

        # Прорисовка окна приложения
        self.setGeometry(0, 0, 1500, 600)
        self.setWindowTitle('Окно администратора')

        self.label = Qt.QLabel('Главное окно')
        self.label.setStyleSheet("color:black; font: bold 20pt 'MS Shell Dlg 2';")
        self.label.setAlignment(Qtt.AlignCenter)

        self.new_face_btn = Qt.QPushButton('Добавление нового пользователя')
        self.check_btn = Qt.QPushButton('Распознать')
        self.list_btn = Qt.QPushButton('Все пользователи')
        self.checklist_btn = Qt.QPushButton('Чек-лист')

        self.button_layout = Qt.QHBoxLayout()
        self.button_layout.addWidget(self.list_btn)
        self.button_layout.addWidget(self.new_face_btn)
        self.button_layout.addWidget(self.check_btn)
        self.button_layout.addWidget(self.checklist_btn)
        self.button_layout.setAlignment(Qtt.AlignCenter)

        self.v_layout = Qt.QVBoxLayout(self)
        self.v_layout.addWidget(self.label)
        self.v_layout.addLayout(self.button_layout)

        # Нажатие кнопки добавления лица
        self.new_face_btn.clicked.connect(make_new)
        # Нажатие кнопки распознавания лица
        self.check_btn.clicked.connect(whois)
        # Нажатие кнопки перехода в список пользователей
        self.list_btn.clicked.connect(go_to_list)

        self.checklist_btn.clicked.connect(self.start_les)

    def start_les(self):
        name, role = whois()
        if role not in ['Преподаватель', 'Администратор']:
            msg = Qt.QMessageBox(Qt.QMessageBox.Critical, "Ошибка!", "Отказано в доступе!", Qt.QMessageBox.Close)
            QTimer.singleShot(5000, msg.close)
            msg.exec_()
        else:
            st = GroupSelection.AddGroups(name, role, parent=self)
            if st.exec_():
                t_lst = st.groups.text()
                #print(t_lst)
                gr_list = t_lst.split(sep="; ")
                gr_list.remove("")
                #print(gr_list)
                ch = CheckStudents.Check(gr_list, connection, cursor)
                ch.exec_()


connection = psycopg2.connect(
        database="maiid",
        user="postgres",
        password="12345",
        host="127.0.0.1",
        port="5432"
    )
cursor = connection.cursor()

if __name__ == '__main__':
    # Подключение к БД
    app = Qt.QApplication(sys.argv)

    font = QFont()
    font.setFamily('MS Shell Dlg 2')
    font.setPointSize(10)

    roles = ['Преподаватель', 'М3О-416Б-19', 'М3О-417Бк-19', 'М3О-418Бк-19', 'Слушатель', 'Роль не выбрана']
    roles.sort()

    w = MainWindow()
    w.show()
    try:
        sys.exit(app.exec_())
    finally:
        connection.close()


