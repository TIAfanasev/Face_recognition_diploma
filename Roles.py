import time
from PyQt5 import Qt, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt as Qtt, QTimer
import shutil
import threading
import pickle

import Var


class Roles(Qt.QDialog):

    def __init__(self, user_id=0):
        super().__init__()
        self.setGeometry(760, 340, 400, 400)
        self.setWindowTitle('Роли - MAI ID')
        self.setWindowIcon(QtGui.QIcon("Icon.png"))
        self.setModal(True)

        self.main_label = Qt.QLabel('Список ролей')
        self.main_label.setStyleSheet("color:#0095DA; font: bold 20pt 'MS Shell Dlg 2';")
        self.main_label.setAlignment(Qtt.AlignCenter)

        self.table = Qt.QTableWidget()

        self.label = Qt.QLabel('Введите новую роль:')
        self.label.setFont(Var.font)

        self.field = Qt.QTextEdit()
        self.field.setFont(Var.font)
        self.field.setPlaceholderText('Пример: М3О-417Бк-19')
        self.field.setFixedHeight(37)

        self.add_btn = Qt.QPushButton('Подтвердить')
        self.add_btn.setFont(Var.font)

        v_layout = Qt.QVBoxLayout(self)
        v_layout.addWidget(self.main_label)
        v_layout.addWidget(self.table)
        v_layout.addWidget(self.label)
        v_layout.addWidget(self.field)
        v_layout.addWidget(self.add_btn)

        self.table_filling()

        self.add_btn.clicked.connect(self.new_role)

    def new_role(self):
        role = self.field.toPlainText().strip()
        if role in Var.roles:
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Роль уже существует!')
        elif not role:
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Введите роль!')
        else:
            Var.roles.append(role)
            f = open("roles", "wb")
            f.write(pickle.dumps(Var.roles))
            f.close()
            self.table_filling()
            self.field.setText("")

    def table_filling(self):

        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Роль", "Удалить"])

        for one_role in Var.roles:
            if one_role != 'Роль не выбрана':
                row_count = self.table.rowCount()
                self.table.insertRow(row_count)

                item = QtWidgets.QTableWidgetItem(one_role)
                item.setTextAlignment(Qtt.AlignCenter)
                self.table.setItem(row_count, 0, item)

                item = Qt.QPushButton('❌')
                item.clicked.connect(self.del_btn)
                self.table.setCellWidget(row_count, 1, item)

        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.table.horizontalHeader().setDefaultAlignment(Qtt.AlignCenter)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

    def del_btn(self):
        role = self.table.item(self.table.currentRow(), 0).text()
        Var.roles.remove(role)
        f = open("roles", "wb")
        f.write(pickle.dumps(Var.roles))
        f.close()
        work_query = f"SELECT * FROM faces WHERE role = '{role.encode('cp866').decode('cp1251')}'"
        Var.cursor.execute(work_query)
        Var.connection.commit()
        records = Var.cursor.fetchall()
        for row in records:
            work_query = f"UPDATE faces SET role = '{'Роль не выбрана'.encode('cp866').decode('cp1251')} WHERE id = {row[0]}"
            Var.cursor.execute(work_query)
            Var.connection.commit()
        self.table_filling()

