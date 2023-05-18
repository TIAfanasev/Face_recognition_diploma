from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QLabel
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import Qt as Qtt
from PyQt5 import Qt
import face_recognition
import pickle
import cv2
import sys


def get_frame_color(counter):
    if counter == 0:
        return 255, 0, 0  # Красный
    elif counter == 1:
        return 255, 165, 0  # Оранжевый
    elif counter == 2:
        return 255, 255, 0  # Желтый
    elif counter == 3:
        return 165, 255, 165  # Желто-зеленый
    elif counter == 4:
        return 0, 255, 165  # Салатовый
    else:
        return 0, 255, 0  # Зеленый


class Ident(Qt.QDialog):
    def __init__(self, table_window=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Распознавание - MAI ID")
        self.setWindowIcon(QIcon("Icon.png"))
        self.setWindowFlags(Qtt.WindowCloseButtonHint)
        self.setGeometry(1250, 250, 666, 506)

        self.image_label = QLabel(self)

        self.data = pickle.loads(open('face_enc', "rb").read())
        self.table_window = table_window

        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)

        self.video_capture = cv2.VideoCapture(0)

        self.closed = False

    def set_image(self, image):
        self.image_label.setPixmap(QPixmap.fromImage(image))

    def recognize_faces(self):

        print("Streaming started")
        conf_count = 0
        t_id = -1
        out_flag = False
        # loop over frames from the video file stream
        while not self.closed:
            # grab the frame from the threaded video stream
            ret, frame = self.video_capture.read()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            names = []  # Список для хранения имен распознанных лиц

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.data["encodings"], face_encoding)
                id_user = -1

                if True in matches:
                    matched_indexes = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    for i in matched_indexes:
                        id_user = self.data["names"][i]
                        counts[id_user] = counts.get(id_user, 0) + 1

                    id_user = max(counts, key=counts.get)

                names.append(id_user)  # Добавляем имя в список имен

                if t_id == id_user and id_user != -1:
                    conf_count += 1
                else:
                    conf_count = 1
                    t_id = id_user
                if conf_count >= 5:
                    # Записываем имя в таблицу в окне TableWindow
                    if self.table_window:
                        self.table_window.add_name(id_user)
                    else:
                        out_flag = True
                        break
                    conf_count = 0

                color = get_frame_color(conf_count)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            h, w, ch = frame.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            image = convert_to_qt_format.scaled(640, 480)

            self.set_image(image)
            if out_flag:
                self.video_capture.release()
                cv2.destroyAllWindows()
                self.close()
                return id_user
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print('Прерывание инициировано пользователем')
                self.video_capture.release()
                cv2.destroyAllWindows()
                self.close()
                return -2

    def closeEvent(self, event):
        self.closed = True
        self.video_capture.release()
        cv2.destroyAllWindows()
        event.accept()
        self.close()


class TableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recognized Faces")

        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(1)  # Устанавливаем один столбец

        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def add_name(self, name):
        row_count = self.table_widget.rowCount()
        self.table_widget.insertRow(row_count)
        item = QTableWidgetItem(name)
        self.table_widget.setItem(row_count, 0, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    table_window = TableWindow()
    table_window.show()
    im = Ident(table_window)
    im.show()
    print(im.recognize_faces())
    if im.disconnect():
        sys.exit(app.exec_())
