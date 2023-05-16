from PyQt5 import Qt
from PyQt5.QtCore import Qt as Qtt, QTimer
import sys

import ident
import GroupSelection
import UserProfile
import AllUsers
import CheckStudents
import Var


def make_new():
    ec = UserProfile.FaceWindow()
    ec.exec_()


def whois():
    idnt = ident.Ident()
    idnt.show()
    user = idnt.recognize_faces()
    if user:
        if user == -1:
            print(f'Распознан неизвестный человек')
            return [0, 0]
        elif user != -2:
            work_query = f'SELECT fio, role FROM faces WHERE id = %s'
            Var.cursor.execute(work_query, (user,))
            Var.connection.commit()
            records = Var.cursor.fetchall()
            fio = bytes(records[0][0], 'cp1251').decode('cp866')
            role = bytes(records[0][1], 'cp1251').decode('cp866')
            print(f'Распознан {fio} ({role})')
            return [fio, role]
    else:
        print('Прерывание распознавания')
        return [0, 0]


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
            st = GroupSelection.AddGroups(parent=self)
            if st.exec_():
                t_lst = st.groups.text()
                # print(t_lst)
                gr_list = t_lst.split(sep="; ")
                gr_list.remove("")
                # print(gr_list)
                ch = CheckStudents.Check(gr_list)
                ch.exec_()


if __name__ == '__main__':
    # Подключение к БД
    app = Qt.QApplication(sys.argv)

    w = MainWindow()
    w.show()
    try:
        sys.exit(app.exec_())
    finally:
        Var.connection.close()
