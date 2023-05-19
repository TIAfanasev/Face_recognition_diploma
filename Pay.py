from PyQt5 import Qt, QtGui
from PyQt5.QtCore import Qt as Qtt, QTimer, QSize

import ident
import Var


class Pay(Qt.QDialog):

    def __init__(self, sum_to_pay=None):
        super().__init__()

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Оплата - MAI ID')
        self.setWindowIcon(QtGui.QIcon("Icon.png"))

        self.label = Qt.QLabel('Произвести оплату')
        self.label.setStyleSheet("color:#0095DA; font: bold 20pt 'MS Shell Dlg 2';")
        self.label.setAlignment(Qtt.AlignHCenter)

        self.image_label = Qt.QLabel()
        pixmap = QtGui.QPixmap('Pay2.png')
        pixmap = pixmap.scaled(QSize(300, 300), Qtt.KeepAspectRatio, Qtt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.resize(300, 300)
        self.image_label.setAlignment(Qtt.AlignCenter)

        self.input_comment = Qt.QLabel("Введите сумму:")
        self.input_comment.setFont(Var.font)

        self.input_field = Qt.QTextEdit()
        self.input_field.setPlaceholderText("Например: 5000 (без копеек)")
        self.input_field.setFixedHeight(33)
        if sum_to_pay:
            self.input_field.setText(sum_to_pay)
        self.input_field.setFont(Var.font)

        self.input_layout = Qt.QHBoxLayout()
        self.input_layout.addWidget(self.input_comment)
        self.input_layout.addWidget(self.input_field)

        self.pay_button = Qt.QPushButton("Распознать и оплатить")
        self.pay_button.setFont(Var.font)


        self.layout = Qt.QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.image_label)
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.pay_button)

        self.pay_button.clicked.connect(self.check_field)

    def check_field(self):
        try:
            int(self.input_field.toPlainText())
        except Exception:
            self.input_field.setText("")
        else:
            self.recognition()

    def recognition(self):
        i = ident.Ident()
        i.show()
        id_user = i.recognize_faces()
        price = int(self.input_field.toPlainText())
        if int(id_user) >= 0:
            work_query = f"SELECT balance FROM faces WHERE id = '{id_user}'"
            Var.cursor.execute(work_query)
            Var.connection.commit()
            records = Var.cursor.fetchall()
            balance = int(records[0][0])
            if balance >= price:
                balance -= price
                work_query = f"UPDATE faces SET balance = '{int(balance)}' WHERE id = {id_user}"
                Var.cursor.execute(work_query)
                Var.connection.commit()
                msg = Qt.QMessageBox(Qt.QMessageBox.Information, "Успешно!", "Оплата осуществлена!", Qt.QMessageBox.Close)
                QTimer.singleShot(5000, msg.close)
                if msg.exec_():
                    self.close()
            else:
                msg = Qt.QMessageBox(Qt.QMessageBox.Warning, "Отказано!", "Недостаточно средств на счете!",
                                     Qt.QMessageBox.Close)
                QTimer.singleShot(5000, msg.close)
                if msg.exec_():
                    self.input_field.setText("")
