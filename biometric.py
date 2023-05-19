import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QDialog
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import Qt as Qtt
import pickle
import cv2
import sys


class Cam(QDialog):
    def __init__(self, new_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Распознавание - MAI ID")
        self.setWindowIcon(QIcon("Icon.png"))
        self.setWindowFlags(Qtt.WindowCloseButtonHint)
        self.setGeometry(1250, 250, 666, 506)
        self.setModal(True)

        self.new_id = new_id

        self.image_label = QLabel(self)

        self.res_flag = 1

        self.data = pickle.loads(open('face_enc', "rb").read())

        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)

        self.video_capture = cv2.VideoCapture(0)

        self.closed = False

    def set_image(self, image):
        self.image_label.setPixmap(QPixmap.fromImage(image))

    def main(self, new_id):

        cascPathface = os.path.dirname(cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
        face_cascade = cv2.CascadeClassifier(cascPathface)

        if not self.video_capture.isOpened():
            print("Cannot open camera")
            sys.exit()

        count = 0
        dir_path = Path.cwd()
        folder = Path(dir_path, 'Images', str(new_id))
        if not os.path.exists(folder):
            os.makedirs(folder)
        skip = 0

        while count < 100:
            if not self.closed:
                ret, frame = self.video_capture.read()
                frame = cv2.flip(frame, 1)
                self.show()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                for (x, y, w, h) in faces:
                    filename = os.path.join(folder, "photo_%d.jpg" % count)
                    cv2.imwrite(filename, frame)
                    count += 1

                cv2.putText(frame, f'{count}/100', (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 139, 210), 2, cv2.LINE_AA)

                h, w, ch = frame.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                image = convert_to_qt_format.scaled(640, 480)

                self.set_image(image)

                if cv2.waitKey(1) == ord('q'):
                    self.res_flag = 0
                    break
                cv2.waitKey(200)
            else:
                break

        self.video_capture.release()
        self.accept()
        return self.res_flag

    def closeEvent(self, event):
        self.closed = True
        self.video_capture.release()
        cv2.destroyAllWindows()
        event.accept()
        self.res_flag = 0
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = Cam(1000)
    dialog.main(1000)
    sys.exit(app.exec_())
