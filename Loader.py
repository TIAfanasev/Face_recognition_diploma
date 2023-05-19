import time

from PyQt5 import Qt, QtGui
from PyQt5.QtCore import Qt as Qtt
import sys


class Movie(Qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGeometry(630, 337, 720, 405)
        self.setFixedSize(720, 405)
        self.setWindowFlag(Qtt.FramelessWindowHint)

        lblgif = Qt.QLabel(self)

        self.movie = QtGui.QMovie('Loader.gif')
        lblgif.setMovie(self.movie)

        self.movie.start()


if __name__ == '__main__':
    app = Qt.QApplication(sys.argv)

    w = Movie()
    w.show()
    sys.exit(app.exec_())
