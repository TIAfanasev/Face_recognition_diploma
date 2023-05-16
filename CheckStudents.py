from PyQt5 import Qt, QtWidgets
from PyQt5.QtCore import Qt as Qtt
import ident
import Var


def table_filling(table, stud=None):
    table.clear()
    table.setRowCount(0)
    table.setColumnCount(1)
    table.setHorizontalHeaderLabels(["ФИО"])
    table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
    table.horizontalHeader().setDefaultAlignment(Qtt.AlignCenter)
    table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)


class Check(Qt.QDialog):

    def __init__(self, group_list):

        super().__init__()
        self.setGeometry(0, 0, 1000, 600)
        self.setWindowTitle('Посещаемость')

        # self.group_list = group_list
        self.labels_list = []
        self.tables_list = []
        self.labels_text = group_list

        for x in group_list:
            self.labels_list.append(Qt.QLabel(x))
            self.tables_list.append(Qt.QTableWidget())
        print(self.labels_list)

        self.label = Qt.QLabel('Студенты')
        self.label.setStyleSheet("color:black; font: bold 20pt 'MS Shell Dlg 2';")
        self.label.setAlignment(Qtt.AlignCenter)

        self.start_btn = Qt.QPushButton()
        self.start_btn.setText("Старт")



        self.v_layout = Qt.QVBoxLayout(self)
        self.v_layout.addWidget(self.label)
        for x in range(len(self.labels_list)):
            self.v_layout.addWidget(self.labels_list[x])
            self.v_layout.addWidget(self.tables_list[x])
        self.v_layout.addWidget(self.start_btn)
        #self.v_layout.addWidget(self.labels_list[x])

        for x in range(len(self.labels_list)):
            table_filling(self.tables_list[x])

        self.start_btn.clicked.connect(self.startstop)

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
            self.ident = ident.Ident(self)
            self.start_btn.setText("Стоп")
            self.ident.closed = False
            self.ident.show()
            self.ident.recognize_faces()
        else:
            self.ident.closed = True
            self.ident.close()
            self.start_btn.setText("Старт")



