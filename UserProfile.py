import time
from PyQt5 import Qt, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt as Qtt, QTimer
import shutil
import threading

import make_cascade
import biometric
import Var
import AllUsers
import Loader


class FaceWindow(Qt.QDialog):

    def __init__(self, user_id=0):
        super().__init__()
        self.setGeometry(0, 0, 1500, 600)
        self.setWindowTitle('Добавление пользователя - MAI ID')
        self.setWindowIcon(QtGui.QIcon("Icon.png"))
        self.setModal(False)

        self.label = Qt.QLabel('Анкета')
        self.label.setStyleSheet("color:black; font: bold 20pt 'MS Shell Dlg 2';")
        self.label.setAlignment(Qtt.AlignCenter)

        self.user_id = user_id

        if user_id == 0:
            self.ID_label = Qt.QLabel('ID: (устанавливается автоматически)')
            self.setWindowTitle('Добавление пользователя')
        else:
            self.ID_label = Qt.QLabel(f'ID: {user_id}')
            self.setWindowTitle('Редактирование пользователя')
        self.ID_label.setFont(Var.font)

        self.FIO_label = Qt.QLabel('ФИО:')
        self.FIO_label.setFont(Var.font)
        self.FIO = Qt.QTextEdit()
        self.FIO.setFont(Var.font)
        self.FIO.setPlaceholderText('Пример: Иванов Иван Иванович')
        #self.fio_cl = one_query('fio', 'clients', self.id_cl)
        #self.FIO.setText(bytes(self.fio_cl, 'cp1251').decode('cp866'))

        self.Role_label = Qt.QLabel('Группа/Должность:')
        self.Role_label.setFont(Var.font)
        self.Role = Qt.QComboBox(self)
        self.Role.setFont(Var.font)
        self.Role.addItems(Var.roles)
        self.Role.setCurrentText('---Выберите роль---')
        #self.Role.setFontPointSize(10)
        # self.phone_cl = one_query('phone', 'clients', self.id_cl)
        #self.Role.setText(self.phone_cl)

        self.Phone_label = Qt.QLabel('Номер телефона:')
        self.Phone_label.setFont(Var.font)
        self.Phone = Qt.QLineEdit()
        self.Phone.setFont(Var.font)
        self.Phone.setInputMask('+7(999)999-99-99;_')

        self.Balance_label = Qt.QLabel('Баланс (₽):')
        self.Balance_label.setFont(Var.font)
        self.Balance = Qt.QTextEdit()
        self.Balance.setFont(Var.font)
        self.Balance.setPlaceholderText("Например: 5000 (без копеек)")

        self.add_face = Qt.QPushButton('Перейти к съемке')
        self.add_face.setFont(Var.font)
        self.confirm = Qt.QPushButton('Подтвердить')
        self.confirm.setFont(Var.font)
        self.cancel = Qt.QPushButton('Отмена')
        self.cancel.setFont(Var.font)

        self.lower_label = Qt.QLabel()
        self.lower_label.setEnabled(False)

        self.add_face.clicked.connect(self.new_face)
        self.confirm.clicked.connect(self.cnf_btn)
        self.cancel.clicked.connect(self.cncl_btn)

        if user_id != 0:
            work_query = f'SELECT fio, role, phone, balance FROM faces WHERE id = %s'
            Var.cursor.execute(work_query, (user_id,))
            Var.connection.commit()
            records = Var.cursor.fetchall()

            self.FIO.setText(records[0][0].encode('cp1251').decode('cp866'))
            self.Role.setCurrentText(records[0][1].encode('cp1251').decode('cp866'))
            self.Phone.setText(records[0][2])
            self.Balance.setText(str(records[0][3]))

            self.add_face.setEnabled(False)
            self.confirm.setEnabled(True)
        else:
            self.confirm.setEnabled(False)
        v_layout = Qt.QVBoxLayout()
        v_layout.addWidget(self.ID_label)
        v_layout.addWidget(self.FIO_label)
        v_layout.addWidget(self.FIO)
        v_layout.addWidget(self.Role_label)
        v_layout.addWidget(self.Role)
        v_layout.addWidget(self.Phone_label)
        v_layout.addWidget(self.Phone)
        v_layout.addWidget(self.Balance_label)
        v_layout.addWidget(self.Balance)
        btn_layout = Qt.QHBoxLayout()
        btn_layout.addWidget(self.confirm)
        btn_layout.addWidget(self.cancel)
        v_layout.addWidget(self.lower_label)
        v_layout.addWidget(self.add_face)
        v_layout.addLayout(btn_layout)
        self.setLayout(v_layout)

    def cnf_btn(self):
        if self.user_id:
            fio = self.FIO.toPlainText().encode('cp866').decode('cp1251')
            role = self.Role.currentText().encode('cp866').decode('cp1251')
            phone = self.Phone.text()[1:]
            phone = int(''.join(filter(str.isdigit, phone))[1:])
            print(phone)
            balance = self.Balance.toPlainText()
            if not (fio and role and balance) or role == 'Роль не выбрана' or phone < 1000000000:
                Qt.QMessageBox.critical(self, 'Ошибка!', 'Заполните все поля!')
            elif not balance.isdigit():
                Qt.QMessageBox.critical(self, 'Ошибка!', 'В поле Баланс \n можно вводить только цифры')
            else:
                work_query = f"UPDATE faces SET fio = '{fio}', role = '{role}', phone = '{phone}', " \
                             f"balance = '{int(balance)}' WHERE id = {self.user_id}"
                Var.cursor.execute(work_query)
                Var.connection.commit()
                self.accept()
        else:
            self.thread = threading.Thread(target=self.calc_emb)
            self.thread.start()

            self.splash = Loader.Movie(parent=self)
            self.splash.exec_()

            self.accept()

    def calc_emb(self):
        make_cascade.update_cascade(self.id_user)
        self.splash.accept()

    def cncl_btn(self):
        if not self.user_id:
            if self.confirm.isEnabled():
                work_query = f"DELETE FROM faces WHERE id = '{self.id_user}'"
                Var.cursor.execute(work_query)
                Var.connection.commit()
                shutil.rmtree(f"Images\\{self.id_user}")
            self.reject()
        else:
            self.reject()

    def new_face(self):
        fio = self.FIO.toPlainText().encode('cp866').decode('cp1251')
        role = self.Role.currentText().encode('cp866').decode('cp1251')
        phone = self.Phone.text()[2:]
        if phone:
            phone = int(''.join(filter(str.isdigit, phone)))
        print(phone)
        balance = self.Balance.toPlainText()
        if not (fio and role and balance) or role == 'Роль не выбрана' or phone < 1000000000:
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Заполните все поля!')
        elif not balance.isdigit():
            Qt.QMessageBox.critical(self, 'Ошибка!', 'В поле Баланс \n можно вводить только цифры')
        else:
            work_query = f'SELECT phone FROM faces WHERE phone = %s'
            Var.cursor.execute(work_query, (str(phone),))
            Var.connection.commit()
            records = Var.cursor.fetchall()
            if records:
                msg = Qt.QMessageBox(Qt.QMessageBox.Critical, "Ошибка!", "Указаный номер телефона уже используется!",
                                     Qt.QMessageBox.Close)
                QTimer.singleShot(5000, msg.close)
                msg.exec_()
            else:
                work_query = f'INSERT INTO faces (fio, role, phone, balance) ' \
                             f'VALUES (\'{fio}\', \'{role}\', \'{phone}\', \'{balance}\')'
                Var.cursor.execute(work_query)
                Var.connection.commit()
                work_query = f'SELECT id FROM faces WHERE fio = %s AND role = %s AND phone = %s'
                Var.cursor.execute(work_query, (fio, role, str(phone),))
                Var.connection.commit()
                records = Var.cursor.fetchall()
                self.id_user = records[0][0]
                self.ID_label.setText(f'ID: {self.id_user}')
                bm = biometric.Cam(self.id_user)
                bm.show()
                if not bm.main(self.id_user):
                    work_query = f'DELETE FROM faces WHERE id = \'{self.id_user}\''
                    Var.cursor.execute(work_query)
                    Var.connection.commit()
                    shutil.rmtree(f"Images\\{self.id_user}")
                    self.lower_label.setText('Ошибка записи')
                    self.lower_label.setStyleSheet("color:red; font: 7pt 'MS Shell Dlg 2';")
                else:
                    self.add_face.setEnabled(False)
                    self.lower_label.setText('Биометрия записана успешно')
                    self.lower_label.setStyleSheet("color:green; font: 7pt 'MS Shell Dlg 2';")
                    self.confirm.setEnabled(True)

                self.lower_label.setEnabled(True)
