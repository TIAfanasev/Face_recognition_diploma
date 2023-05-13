from PyQt5 import Qt
from PyQt5.QtCore import Qt as Qtt
import make_cascade
import shutil
import psycopg2
from PyQt5.QtGui import QFont
import biometric


class FaceWindow(Qt.QDialog):

    def __init__(self, user_id=0):
        super().__init__()
        self.setGeometry(0, 0, 1500, 600)
        self.setWindowTitle('Добавление пользователя')

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
        self.ID_label.setFont(font)

        self.FIO_label = Qt.QLabel('ФИО:')
        self.FIO_label.setFont(font)
        self.FIO = Qt.QTextEdit()
        self.FIO.setFont(font)
        self.FIO.setPlaceholderText('Пример: Иванов Иван Иванович')
        #self.fio_cl = one_query('fio', 'clients', self.id_cl)
        #self.FIO.setText(bytes(self.fio_cl, 'cp1251').decode('cp866'))

        self.Role_label = Qt.QLabel('Группа/Должность:')
        self.Role_label.setFont(font)
        self.Role = Qt.QComboBox(self)
        self.Role.setFont(font)
        self.Role.addItems(roles)
        self.Role.setCurrentText('---Выберите роль---')
        #self.Role.setFontPointSize(10)
        # self.phone_cl = one_query('phone', 'clients', self.id_cl)
        #self.Role.setText(self.phone_cl)

        self.Phone_label = Qt.QLabel('Номер телефона:')
        self.Phone_label.setFont(font)
        self.Phone = Qt.QTextEdit()
        self.Phone.setFont(font)
        self.Phone.setPlaceholderText('Номер телефона в формате +7XXXXXXXXXX')
        # self.phone_cl = one_query('phone', 'clients', self.id_cl)
        #self.Phone.setText('+7' + self.phone_cl)

        self.Balance_label = Qt.QLabel('Баланс (₽):')
        self.Balance_label.setFont(font)
        self.Balance = Qt.QTextEdit()
        self.Balance.setFont(font)

        self.add_face = Qt.QPushButton('Перейти к съемке')
        self.confirm = Qt.QPushButton('Подтвердить')
        self.cancel = Qt.QPushButton('Отмена')
        self.delete = Qt.QPushButton('Удалить')
        self.delete.setStyleSheet('background-color: #DB4139; border-radius: 6px; color: white;'
                                  'min-width: 10em; padding: 4px')

        self.lower_label = Qt.QLabel()
        self.lower_label.setEnabled(False)

        self.add_face.clicked.connect(self.new_face)
        self.confirm.clicked.connect(self.cnf_btn)
        self.cancel.clicked.connect(self.cncl_btn)

        if user_id != 0:
            work_query = f'SELECT fio, role, phone, balance FROM faces WHERE id = %s'
            cursor.execute(work_query, (user_id,))
            connection.commit()
            records = cursor.fetchall()

            self.FIO.setText(records[0][0].encode('cp1251').decode('cp866'))
            self.Role.setCurrentText(records[0][1].encode('cp1251').decode('cp866'))
            self.Phone.setText('+7' + records[0][2])
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
        v_layout.addWidget(self.delete)
        self.setLayout(v_layout)

    def cnf_btn(self):
        if self.user_id:
            fio = self.FIO.toPlainText().encode('cp866').decode('cp1251')
            role = self.Role.currentText().encode('cp866').decode('cp1251')
            phone = self.Phone.toPlainText()
            balance = self.Balance.toPlainText()
            if not (fio and role and phone) or role == '---Выберите роль---':
                Qt.QMessageBox.critical(self, 'Ошибка!', 'Заполните все поля!')
            elif not (phone[0:2] == '+7' and len(phone[2:]) == 10 and phone[2:].isdigit()):
                Qt.QMessageBox.critical(self, 'Ошибка!', 'Введите номер в формате: \n +7ХХХХХХХХХХ')
            elif not balance.isdigit():
                Qt.QMessageBox.critical(self, 'Ошибка!', 'В поле Баланс \n можно вводить только цифры')
            else:
                phone = phone[2:]
                work_query = f"UPDATE faces SET fio = '{fio}', role = '{role}', phone = '{phone}', " \
                             f"balance = '{int(balance)}' WHERE id = {self.user_id}"
                cursor.execute(work_query)
                connection.commit()
        else:
            make_cascade.update_cascade(self.id_user)
        self.accept()

    def cncl_btn(self):
        if not self.user_id:
            if self.confirm.isEnabled():
                work_query = f"DELETE FROM faces WHERE id = '{self.id_user}'"
                cursor.execute(work_query)
                connection.commit()
                shutil.rmtree(f"Images\\{self.id_user}")
            self.reject()
        else:
            self.reject()

    def new_face(self):
        fio = self.FIO.toPlainText().encode('cp866').decode('cp1251')
        role = self.Role.currentText().encode('cp866').decode('cp1251')
        phone = self.Phone.toPlainText()
        balance = self.Balance.toPlainText()
        if not (fio and role and phone) or role == 'Роль не выбрана':
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Заполните все поля!')
        elif not (phone[0:2] == '+7' and len(phone[2:]) == 10 and phone[2:].isdigit()):
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Введите номер в формате: \n +7ХХХХХХХХХХ')
        else:
            phone = phone [2:]
            work_query = f'INSERT INTO faces (fio, role, phone) ' \
                         f'VALUES (\'{fio}\', \'{role}\', \'{phone}\')'
            cursor.execute(work_query)
            connection.commit()
            work_query = f'SELECT id FROM faces WHERE fio = %s AND role = %s AND phone = %s'
            cursor.execute(work_query, (fio, role, phone,))
            connection.commit()
            records = cursor.fetchall()
            self.id_user = records[0][0]
            self.ID_label.setText(f'ID: {self.id_user}')
            if not biometric.__init__(self.id_user):
                work_query = f'DELETE FROM faces WHERE id = \'{self.id_user}\''
                cursor.execute(work_query)
                connection.commit()
                shutil.rmtree(f"Images\\{self.id_user}")
                self.lower_label.setText('Ошибка записи')
                self.lower_label.setStyleSheet("color:red; font: 7pt 'MS Shell Dlg 2';")
            else:
                self.add_face.setEnabled(False)
                self.lower_label.setText('Биометрия записана успешно')
                self.lower_label.setStyleSheet("color:green; font: 7pt 'MS Shell Dlg 2';")
                self.confirm.setEnabled(True)

            self.lower_label.setEnabled(True)


connection = psycopg2.connect(
        database="maiid",
        user="postgres",
        password="12345",
        host="127.0.0.1",
        port="5432"
    )
cursor = connection.cursor()

font = QFont()
font.setFamily('MS Shell Dlg 2')
font.setPointSize(10)

roles = ['Преподаватель', 'М3О-416Б-19', 'М3О-417Бк-19', 'М3О-418Бк-19', 'Слушатель', 'Роль не выбрана']
roles.sort()
