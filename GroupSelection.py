from PyQt5 import Qt, QtWidgets
from PyQt5.QtCore import Qt as Qtt

import Var


class AddGroups(Qt.QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setGeometry(0, 0, 1000, 600)
        self.setWindowTitle('Посещаемость')

        self.group_list = []
        self.roles_copy = list(Var.roles)

        self.label = Qt.QLabel('Выберите группу(-ы)')
        self.label.setStyleSheet("color:black; font: bold 20pt 'MS Shell Dlg 2';")
        self.label.setAlignment(Qtt.AlignCenter)

        self.groups = Qt.QLabel()
        self.groups.setFont(Var.font)

        self.table = Qt.QTableWidget()
        self.table.setFont(Var.font)

        self.start = Qt.QPushButton('Старт!')
        self.start.setFont(Var.font)

        self.v_layout = Qt.QVBoxLayout(self)
        self.v_layout.addWidget(self.label)
        self.v_layout.addWidget(self.groups)
        self.v_layout.addWidget(self.table)
        self.v_layout.addWidget(self.start)

        self.gr_table()

        self.start.clicked.connect(self.start_btn)

    def gr_table(self):

        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Группа", "Добавить"])

        for x in self.roles_copy:
            if x[0].isdigit() or x[1].isdigit() or x == 'Преподаватель': #Обязательно убрать!
                row_count = self.table.rowCount()
                self.table.insertRow(row_count)

                item = QtWidgets.QTableWidgetItem(x)
                item.setTextAlignment(Qtt.AlignCenter)
                self.table.setItem(row_count, 0, item)

                item = Qt.QPushButton('+')
                item.clicked.connect(self.add_btn)
                self.table.setCellWidget(row_count, 1, item)

        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setDefaultAlignment(Qtt.AlignCenter)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

    def add_btn(self):
        gr = self.table.item(self.table.currentRow(), 0).text()
        self.group_list.append(gr)
        self.roles_copy.remove(gr)
        t_groups = self.groups.text()
        self.groups.setText(t_groups + gr + "; ")
        self.gr_table()

    def start_btn(self):
        self.accept()


