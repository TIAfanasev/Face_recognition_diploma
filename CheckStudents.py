from PyQt5 import Qt, QtWidgets
from PyQt5.QtCore import Qt as Qtt, QTimer
import subprocess
from PyQt5.QtGui import QFont
import sys
import multiprocessing
import GroupSelection
import UserProfile
import AllUsers
import biometric
import make_cascade
import ident
import psycopg2
import shutil
from threading import Thread
import time


class Check(Qt.QDialog):

    def __init__(self, group_list, connection, cursor):

        super().__init__()
        self.setGeometry(0, 0, 1000, 600)
        self.setWindowTitle('Посещаемость')

        self.cursor = cursor
        self.connection = connection

        # self.group_list = group_list
        self.labels_list = []
        self.tables_list = []

        for x in group_list:
            self.labels_list.append(Qt.QLabel(x))
            self.tables_list.append(Qt.QTableWidget())
        print(self.labels_list)

        self.label = Qt.QLabel('Студенты')
        self.label.setStyleSheet("color:black; font: bold 20pt 'MS Shell Dlg 2';")
        self.label.setAlignment(Qtt.AlignCenter)

        self.v_layout = Qt.QVBoxLayout(self)
        self.v_layout.addWidget(self.label)
        for x in range(len(self.labels_list)):
            self.v_layout.addWidget(self.labels_list[x])
            self.v_layout.addWidget(self.tables_list[x])
        #self.v_layout.addWidget(self.labels_list[x])
        for x in range(len(self.labels_list)):
            self.table_filling(self.tables_list[x])
        self.start()

    def table_filling(self, table, stud=None):
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["ФИО"])
        table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        table.horizontalHeader().setDefaultAlignment(Qtt.AlignCenter)
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        if stud:
            row_count = self.table.rowCount()
            self.table.insertRow(row_count)

            item = QtWidgets.QTableWidgetItem(str(stud))
            item.setTextAlignment(Qtt.AlignCenter)
            self.table.setItem(row_count, 0, item)

    def start(self):
        q = multiprocessing.Queue()
        t1 = Thread(target=self.prnt, args=(q,))
        t2 = Thread(target=ident.__init__, args=(q, True,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def prnt(self, qu):
        fl = qu.get()
        while fl != -2:
            if fl != -1:
                print(fl)
                work_query = f"SELECT fio, role FROM faces WHERE id = '{fl}'"
                self.cursor.execute(work_query)
                self.connection.commit()
                records = self.cursor.fetchall()
                fio = records[0][0].encode('cp1251').decode('cp866')
                role = records[0][1].encode('cp1251').decode('cp866')
                print(role)
                if self.labels_list.index(role):
                    self.table_filling(self.tables_list[self.labels_list.index(role)], stud=fio)
            time.sleep(2)
            fl = qu.get()


#if __name__ == '__main__':



