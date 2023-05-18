from PyQt5 import Qt, QtWidgets, QtGui
from PyQt5.QtCore import Qt as Qtt
import UserProfile
import shutil

import Var
import make_cascade


class AllUsersWindow(Qt.QDialog):

    def __init__(self):

        super().__init__()
        self.setGeometry(0, 0, 1500, 600)
        self.setWindowTitle('Список всех пользователей - MAI ID')
        self.setWindowIcon(QtGui.QIcon("Icon.png"))

        self.label = Qt.QLabel('Все пользователи')
        self.label.setStyleSheet("color:black; font: bold 20pt 'MS Shell Dlg 2';")
        self.label.setAlignment(Qtt.AlignCenter)

        self.search_label = Qt.QLabel('Поиск:')
        self.search_label.setFont(Var.font)

        self.search_field = Qt.QTextEdit()
        self.search_field.setPlaceholderText('Введите строку для поиска')
        self.search_field.setFixedHeight(32)
        self.search_field.setFont(Var.font)

        self.search_button = Qt.QPushButton('Найти!')
        self.search_button.setFont(Var.font)
        self.search_button.setStyleSheet('color: #0095DA;')

        self.select_role = Qt.QComboBox(self)
        self.select_role.addItems(Var.roles)
        self.select_role.setFont(Var.font)
        self.select_role.setCurrentText('Роль не выбрана')

        self.table = Qt.QTableWidget()

        self.search_layout = Qt.QHBoxLayout()
        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_field)
        self.search_layout.addWidget(self.search_button)

        self.v_layout = Qt.QVBoxLayout(self)
        self.v_layout.addLayout(self.search_layout)
        self.v_layout.addWidget(self.select_role)
        self.v_layout.addWidget(self.table)

        self.start_fil()

        self.select_role.currentTextChanged.connect(self.start_fil)
        self.search_button.clicked.connect(self.search)

    def start_fil(self):
        self.table_filling()

    def search(self):
        if self.search_field.toPlainText() == '':
            self.table_filling()
        else:
            self.table_filling(1)
        self.search_field.setText("")

    def table_filling(self, from_btn=0):

        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Роль", "Телефон", "Баланс", "Изменить", "Удалить"])

        role_now = self.select_role.currentText()
        search = self.search_field.toPlainText().encode('cp866').decode('cp1251')
        if role_now == 'Роль не выбрана':
            if from_btn == 0:
                display_query = 'SELECT * FROM faces ORDER BY role DESC, fio DESC'
            else:
                display_query = f"SELECT * FROM faces WHERE fio LIKE '%{search}%' ORDER BY role DESC, fio DESC"
        elif from_btn == 0:
            display_query = f"SELECT * FROM faces WHERE role = '{role_now.encode('cp866').decode('cp1251')}' " \
                            f"ORDER BY fio DESC"
        else:
            display_query = f"SELECT * FROM faces WHERE role = '{role_now.encode('cp866').decode('cp1251')}' " \
                            f"AND fio LIKE '%{search}%' ORDER BY fio DESC"

        Var.cursor.execute(display_query)
        Var.connection.commit()
        records = Var.cursor.fetchall()

        for row in records:
            row_count = self.table.rowCount()
            self.table.insertRow(row_count)

            item = QtWidgets.QTableWidgetItem(str(row[0]))
            item.setTextAlignment(Qtt.AlignCenter)
            self.table.setItem(row_count, 0, item)

            item = QtWidgets.QTableWidgetItem(bytes(row[1], 'cp1251').decode('cp866'))
            item.setTextAlignment(Qtt.AlignCenter)
            self.table.setItem(row_count, 1, item)

            item = QtWidgets.QTableWidgetItem(bytes(row[2], 'cp1251').decode('cp866'))
            item.setTextAlignment(Qtt.AlignCenter)
            self.table.setItem(row_count, 2, item)

            item = QtWidgets.QTableWidgetItem('+7' + str(row[3]))
            item.setTextAlignment(Qtt.AlignCenter)
            self.table.setItem(row_count, 3, item)

            item = QtWidgets.QTableWidgetItem(str(row[4]))
            item.setTextAlignment(Qtt.AlignCenter)
            self.table.setItem(row_count, 4, item)

            item = Qt.QPushButton('✍')
            item.clicked.connect(self.edit_btn)
            self.table.setCellWidget(row_count, 5, item)

            item = Qt.QPushButton('❌')
            item.clicked.connect(self.del_btn)
            self.table.setCellWidget(row_count, 6, item)

            self.table.setRowHeight(row_count, 40)

        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.table.horizontalHeader().setDefaultAlignment(Qtt.AlignCenter)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        headers_for_resize = [0, 3, 4, 5, 6]
        for i in headers_for_resize:
            self.table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)

    def edit_btn(self):
        editor = UserProfile.FaceWindow(int(self.table.item(self.table.currentRow(), 0).text()))
        if editor.exec_():
            self.table_filling()

    def del_btn(self):
        usr = int(self.table.item(self.table.currentRow(), 0).text())
        msg = Qt.QMessageBox.warning(self, 'Удаление', 'Это действие нельзя отменить \n Продолжить?',
                                     Qt.QMessageBox.Yes | Qt.QMessageBox.Cancel, Qt.QMessageBox.Cancel)
        if msg == Qt.QMessageBox.Yes:
            work_query = f"DELETE FROM faces WHERE id = '{usr}'"
            Var.cursor.execute(work_query)
            Var.connection.commit()
            try:
                shutil.rmtree(f"Images\\{usr}")
                make_cascade.del_elem(usr)
            finally:
                self.table_filling()


