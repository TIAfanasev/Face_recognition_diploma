from PyQt5 import Qt, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt as Qtt, QSize, QTimer
from openpyxl import Workbook
import datetime
import os

import ident
import Var


def table_filling(table):
    table.clear()
    table.setRowCount(0)
    table.setColumnCount(1)
    table.setHorizontalHeaderLabels(["ФИО"])
    table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
    table.horizontalHeader().setDefaultAlignment(Qtt.AlignCenter)
    table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)


class Check(Qt.QDialog):

    def __init__(self, group_list, teacher):

        super().__init__()
        self.setGeometry(0, 0, 1000, 600)
        self.setWindowTitle('Посещаемость - MAI ID')
        self.setWindowIcon(QIcon("Icon.png"))

        # self.group_list = group_list
        self.labels_list = []
        self.tables_list = []
        self.labels_text = group_list
        self.teacher = teacher

        for x in group_list:
            self.labels_list.append(Qt.QLabel(x))
            self.tables_list.append(Qt.QTableWidget())
        print(self.labels_list)

        self.label = Qt.QLabel('Студенты')
        self.label.setStyleSheet("color:black; font: bold 20pt 'MS Shell Dlg 2';")
        self.label.setAlignment(Qtt.AlignCenter)

        self.label = Qt.QLabel(f'Преподаватель: {self.teacher}')
        self.label.setStyleSheet("color:black; font: 10pt 'MS Shell Dlg 2';")
        self.label.setAlignment(Qtt.AlignRight)

        self.start_btn = Qt.QPushButton()
        self.start_btn.setText("Старт")

        self.excel_btn = Qt.QPushButton()
        self.excel_btn.setIcon(QIcon('Excel.png'))
        self.excel_btn.setIconSize(QSize(40, 40))
        self.excel_btn.setFixedSize(40, 40)
        self.excel_btn.setStyleSheet('{background-color: #FFFFFF; '
                                     'border-width: 0px; '
                                     'border-radius: 6px; '
                                     'border-color: #FFFFFF;')

        self.excel_layout = Qt.QVBoxLayout()
        self.excel_layout.addWidget(self.excel_btn)
        self.excel_layout.setAlignment(Qtt.AlignRight)

        self.v_layout = Qt.QVBoxLayout(self)
        self.v_layout.addWidget(self.label)
        self.v_layout.addLayout(self.excel_layout)
        for x in range(len(self.labels_list)):
            self.v_layout.addWidget(self.labels_list[x])
            self.v_layout.addWidget(self.tables_list[x])
        self.v_layout.addWidget(self.start_btn)
        #self.v_layout.addWidget(self.labels_list[x])

        for x in range(len(self.labels_list)):
            table_filling(self.tables_list[x])

        self.start_btn.clicked.connect(self.startstop)

        self.excel_btn.clicked.connect(self.excel_export)

    def add_name(self, id_user):
        work_query = f"SELECT fio, role FROM faces WHERE id = '{id_user}'"
        Var.cursor.execute(work_query)
        Var.connection.commit()
        records = Var.cursor.fetchall()
        fio = records[0][0].encode('cp1251').decode('cp866')
        role = records[0][1].encode('cp1251').decode('cp866')
        if role in self.labels_text:
            table = self.tables_list[self.labels_text.index(role)]
            row_count = table.rowCount()
            stop_flag = False
            for i in range(row_count):
                if table.item(i, 0).text() == fio:
                    stop_flag = True
            if not stop_flag:
                table.insertRow(row_count)
                item = Qt.QTableWidgetItem(fio)
                table.setItem(row_count, 0, item)

    def startstop(self):
        if self.start_btn.text() == "Старт":
            #self.start_btn.setEnabled(False)
            self.start_btn.setText("Стоп")
            self.ident = ident.Ident(self)
            self.ident.closed = False
            self.ident.show()
            self.ident.recognize_faces()
        else:
            self.ident.closed = True
            self.ident.close()
            self.start_btn.setText("Старт")

    def excel_export(self):
        if not os.path.exists(f'{str(self.teacher)}'):
            os.mkdir(f'{str(self.teacher)}')
        # Создаем новую рабочую книгу
        workbook = Workbook()
        sheet = workbook.active

        # Копируем данные из QTableWidget в рабочую книгу
        current_row = 1
        fio_column = 'A'
        check_column = 'B'
        for group in self.labels_text:
            work_query = f"SELECT fio FROM faces WHERE role = '{group.encode('cp866').decode('cp1251')}'"
            Var.cursor.execute(work_query)
            Var.connection.commit()
            records = Var.cursor.fetchall()
            table = self.tables_list[self.labels_text.index(group)]
            students = []
            for x in records:
                students.append(x[0].encode('cp1251').decode('cp866'))
            students.sort()
            st_in_class = []
            for row in range(table.rowCount()):
                st_in_class.append(table.item(row, 0).text())
            sheet[fio_column + str(current_row)] = group
            current_row += 1
            for st in range(len(students)):
                sheet[fio_column + str(current_row)] = students[st]
                if students[st] in st_in_class:
                    sheet[check_column + str(current_row)] = '+'
                else:
                    sheet[check_column + str(current_row)] = 'Н'
                current_row += 1
            current_row += 2

        # Сохраняем рабочую книгу
        dt = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        full_folder_path = os.path.join(os.getcwd(), f'{str(self.teacher)}', f'{str(dt)}.xlsx')
        workbook.save(full_folder_path)

        msg = Qt.QMessageBox(Qt.QMessageBox.Information, "Выполнено!", "Excel-таблица сохранена!", Qt.QMessageBox.Close)
        QTimer.singleShot(5000, msg.close)
        msg.setIcon(QIcon("Icon.png"))
        msg.exec_()



