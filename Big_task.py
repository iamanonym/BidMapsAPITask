import requests
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys

map_params = {'ll': '58.980282,53.407158',
              'z': 10, 'l': 'map'}
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
map_api_server = "http://static-maps.yandex.ru/1.x/"


def change_picture(map_params):
    response = requests.get(map_api_server, params=map_params)
    map_file = "map.png"

    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)


class BigTask(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Big_task.ui', self)
        self.map_params = map_params
        self.draw()

    def draw(self):
        self.picture = QPixmap('map.png')
        self.lbl.setPixmap(self.picture)
        self.lbl.adjustSize()
        self.resize(self.picture.width() + 40, self.picture.height() + 40)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.map_params['z'] = self.map_params['z'] - 1
            if self.map_params['z'] < 0:
                self.map_params['z'] = 0
        if event.key() == Qt.Key_PageDown:
            self.map_params['z'] = self.map_params['z'] + 1
            if self.map_params['z'] > 17:
                self.map_params['z'] = 17
        change_picture(self.map_params)
        self.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    bt = BigTask()
    bt.show()
    sys.exit(app.exec_())
