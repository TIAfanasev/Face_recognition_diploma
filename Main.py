from PyQt5 import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt as Qtt, QTimer, QSize
import sys

import ident
import GroupSelection
import UserProfile
import AllUsers
import CheckStudents
import Var
import Pay
import Roles


def make_new():
    ec = UserProfile.FaceWindow()
    ec.exec_()


def start_stream():
    s = ident.Ident(stream=True)
    s.show()
    end = s.recognize_faces()


def whois():
    idnt = ident.Ident()
    idnt.show()
    user = idnt.recognize_faces()
    if user:
        if user == -1:
            print(f'Распознан неизвестный человек')
            msg = Qt.QMessageBox(Qt.QMessageBox.Information, "Успешно!", f'Распознан неизвестный человек',
                                 Qt.QMessageBox.Close)
            msg.setWindowIcon(QIcon("Icon.png"))
            QTimer.singleShot(5000, msg.close)
            if msg.exec_():
                return [0, 0]
        elif user != -2:
            work_query = f'SELECT fio, role FROM faces WHERE id = %s'
            Var.cursor.execute(work_query, (user,))
            Var.connection.commit()
            records = Var.cursor.fetchall()
            fio = bytes(records[0][0], 'cp1251').decode('cp866')
            role = bytes(records[0][1], 'cp1251').decode('cp866')
            print(f'Распознан {fio} ({role})')
            msg = Qt.QMessageBox(Qt.QMessageBox.Information, "Успешно!", f'Распознан {fio} ({role})',
                                 Qt.QMessageBox.Close)
            msg.setWindowIcon(QIcon("Icon.png"))
            QTimer.singleShot(5000, msg.close)
            if msg.exec_():
                return [fio, role]
    else:
        print('Прерывание распознавания')
        msg = Qt.QMessageBox(Qt.QMessageBox.Warning, "Внимание!", f'Распознавание прервано', Qt.QMessageBox.Close)
        msg.setWindowIcon(QIcon("Icon.png"))
        QTimer.singleShot(5000, msg.close)
        if msg.exec_():
            return [0, 0]


def go_to_list():
    lw = AllUsers.AllUsersWindow()
    lw.exec_()


def pay_mai():
    p = Pay.Pay()
    p.exec_()


def add_role():
    t = Roles.Roles()
    t.exec_()


class MainWindow(Qt.QMainWindow):

    def __init__(self):
        super().__init__()

        # Прорисовка окна приложения
        self.setGeometry(0, 0, 1500, 600)
        self.setWindowTitle('Окно администратора - MAI ID')
        self.setWindowIcon(QIcon("Icon.png"))

        central_widget = Qt.QWidget()
        self.setCentralWidget(central_widget)

        self.label = Qt.QLabel()
        pixmap = QPixmap('Logo.png')
        pixmap = pixmap.scaled(QSize(600, 600), Qtt.KeepAspectRatio, Qtt.SmoothTransformation)
        self.label.setPixmap(pixmap)
        self.label.resize(600, 600)
        self.label.setAlignment(Qtt.AlignCenter)

        self.new_face_btn = Qt.QPushButton('Добавить пользователя')
        self.new_face_btn.setIcon(QIcon('Add.png'))
        self.new_face_btn.setIconSize(QSize(50, 50))
        self.new_face_btn.setFont(Var.font)
        self.new_face_btn.setStyleSheet(Var.qss)

        self.check_btn = Qt.QPushButton('Распознать пользователя')
        self.check_btn.setIcon(QIcon('face.png'))
        self.check_btn.setIconSize(QSize(50, 50))
        self.check_btn.setFont(Var.font)
        self.check_btn.setStyleSheet(Var.qss)

        self.access_btn = Qt.QPushButton('Контроль доступа')
        #self.check_btn.setIcon(QIcon('face.png'))
        #self.check_btn.setIconSize(QSize(50, 50))
        self.access_btn.setFont(Var.font)
        self.access_btn.setStyleSheet(Var.qss)

        self.list_btn = Qt.QPushButton('Все пользователи')
        self.list_btn.setIcon(QIcon('Users.png'))
        self.list_btn.setIconSize(QSize(50, 50))
        self.list_btn.setFont(Var.font)
        self.list_btn.setStyleSheet(Var.qss)

        self.checklist_btn = Qt.QPushButton('Отметить посещение')
        self.checklist_btn.setIcon(QIcon('Check.png'))
        self.checklist_btn.setIconSize(QSize(50, 50))
        self.checklist_btn.setFont(Var.font)
        self.checklist_btn.setStyleSheet(Var.qss)

        self.pay_btn = Qt.QPushButton('Оплата')
        self.pay_btn.setIcon(QIcon('Pay.png'))
        self.pay_btn.setIconSize(QSize(50, 50))
        self.pay_btn.setFont(Var.font)
        self.pay_btn.setStyleSheet(Var.qss)

        self.add_role_btn = Qt.QPushButton('Добавить роль')
        self.add_role_btn.setIconSize(QSize(50, 50))
        self.add_role_btn.setFont(Var.font)
        self.add_role_btn.setStyleSheet(Var.qss)

        self.button_layout = Qt.QVBoxLayout()
        self.button_layout.addWidget(self.list_btn)
        self.button_layout.addWidget(self.new_face_btn)
        self.button_layout.addWidget(self.check_btn)
        self.button_layout.addWidget(self.access_btn)
        self.button_layout.addWidget(self.checklist_btn)
        self.button_layout.addWidget(self.pay_btn)
        self.button_layout.addWidget(self.add_role_btn)
        #self.button_layout.addStretch(1)
        self.btn_layout = Qt.QHBoxLayout()
        self.btn_layout.addLayout(self.button_layout)
        self.btn_layout.setAlignment(Qtt.AlignCenter)

        self.v_layout = Qt.QHBoxLayout()
        self.v_layout.addWidget(self.label)
        self.v_layout.addLayout(self.btn_layout)
        self.v_layout.setAlignment(Qtt.AlignVCenter)

        central_widget.setLayout(self.v_layout)

        # Нажатие кнопки добавления лица
        self.new_face_btn.clicked.connect(make_new)
        # Нажатие кнопки распознавания лица
        self.check_btn.clicked.connect(whois)
        # Нажатие кнопки перехода в список пользователей
        self.list_btn.clicked.connect(go_to_list)

        self.checklist_btn.clicked.connect(self.start_les)

        self.pay_btn.clicked.connect(pay_mai)

        self.add_role_btn.clicked.connect(add_role)

        self.access_btn.clicked.connect(start_stream)

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
                ch = CheckStudents.Check(gr_list, name)
                ch.exec_()


if __name__ == '__main__':

    app = Qt.QApplication(sys.argv)

    stylesheet = """
        QMainWindow {
            background-image: url("sky.jpg"); 
            background-repeat: no-repeat; 
            background-position: center;
        }
    """

    app.setStyleSheet(stylesheet)

    w = MainWindow()
    w.showMaximized()
    try:
        sys.exit(app.exec_())
    finally:
        Var.connection.close()
