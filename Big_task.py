import requests
from PyQt5.QtWidgets import QMainWindow, QApplication, \
    QWidget, QGraphicsScene, QGraphicsPixmapItem
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QByteArray
import sys

map_params = {'ll': '58.980282,53.407158',
              'z': 10, 'l': 'map'}
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
map_api_server = "http://static-maps.yandex.ru/1.x/"


def change_picture(map_params):
    response = requests.get(map_api_server, params=map_params)
    file = response.content
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray(file))
    return pixmap


class BigTask(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Big_task.ui', self)
        self.map_params = map_params
        self.picture = None
        self.draw()

        self.map.clicked.connect(self.choose_map)
        self.sat.clicked.connect(self.choose_sat)
        self.skl.clicked.connect(self.choose_skl)

    def choose_map(self):
        self.map_params['l'] = 'map'
        self.picture = change_picture(self.map_params)
        self.draw()

    def choose_sat(self):
        self.map_params['l'] = 'sat'
        self.picture = change_picture(self.map_params)
        self.draw()

    def choose_skl(self):
        self.map_params['l'] = 'skl'
        self.picture = change_picture(self.map_params)
        self.draw()

    def draw(self):
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 600, 450)
        self.view.setScene(self.scene)
        self.scene.addItem(QGraphicsPixmapItem(self.picture))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.map_params['z'] = self.map_params['z'] - 1
            if self.map_params['z'] < 0:
                self.map_params['z'] = 0
        if event.key() == Qt.Key_PageDown:
            self.map_params['z'] = self.map_params['z'] + 1
            if self.map_params['z'] > 17:
                self.map_params['z'] = 17
        if event.key() == Qt.Key_Up:
            ll = list(map(float, self.map_params['ll'].split(',')))
            z = self.map_params['z']
            ll[1] += 0.05 / (2 ** (z - 10))
            if ll[1] >= 85:
                ll[1] = 85.0
            self.map_params['ll'] = '{},{}'.format(*ll)
        if event.key() == Qt.Key_Down:
            ll = list(map(float, self.map_params['ll'].split(',')))
            z = self.map_params['z']
            ll[1] -= 0.05 / (2 ** (z - 10))
            if ll[1] <= -85:
                ll[1] = -85.0
            self.map_params['ll'] = '{},{}'.format(*ll)
        if event.key() == Qt.Key_Right:
            ll = list(map(float, self.map_params['ll'].split(',')))
            z = self.map_params['z']
            ll[0] += 0.05 / (2 ** (z - 10))
            if ll[0] >= 175:
                ll[0] = 175.0
            self.map_params['ll'] = '{},{}'.format(*ll)
        if event.key() == Qt.Key_Left:
            ll = list(map(float, self.map_params['ll'].split(',')))
            z = self.map_params['z']
            ll[0] -= 0.05 / (2 ** (z - 10))
            if ll[0] <= -175:
                ll[0] = -175.0
            self.map_params['ll'] = '{},{}'.format(*ll)
        self.picture = change_picture(self.map_params)
        self.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    bt = BigTask()
    bt.show()
    sys.exit(app.exec_())
