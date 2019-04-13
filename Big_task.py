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
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"


def change_picture(map_params):
    response = requests.get(map_api_server, params=map_params)
    file = response.content
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray(file))
    return pixmap


def get_params(obj, arg_l, arg_z,
               radio=None, booly=False):
    toponym = \
        obj["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "z": arg_z,
        "l": arg_l,
        "pt": "{},{},pm2dbm".format(toponym_longitude, toponym_lattitude)
    }

    if not booly:
        return map_params
    else:
        if radio:
            try:
                return \
                    map_params, \
                    toponym["metaDataProperty"]["GeocoderMetaData"]["text"], \
                    toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
            except KeyError:
                return map_params,  \
                       toponym["metaDataProperty"]["GeocoderMetaData"]["text"], \
                       None
        else:
            return \
                map_params, \
                toponym["metaDataProperty"]["GeocoderMetaData"]["text"]


def get_name(params):
    obj = requests.get(geocoder_api_server, params=params).json()
    toponym = \
        obj["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    try:
        return toponym["metaDataProperty"]["GeocoderMetaData"]["text"], \
            toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
    except KeyError:
        return toponym["metaDataProperty"]["GeocoderMetaData"]["text"], None


class BigTask(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Big_task.ui', self)
        self.map_params = map_params
        self.picture = change_picture(map_params)
        self.index = None
        self.text = ''
        self.draw()

        self.map.clicked.connect(self.choose_map)
        self.sat.clicked.connect(self.choose_sat)
        self.skl.clicked.connect(self.choose_skl)
        self.search.clicked.connect(self.searching)
        self.waster.clicked.connect(self.waste)
        self.rad1.toggled.connect(self.indexing)
        self.rad2.toggled.connect(self.indexing)

    def indexing(self):
        if self.rad1.isChecked:
            if self.text and self.index:
                if not self.text.endswith(self.index):
                    self.text += ', {}'.format(self.index)
                    self.line2.setText(self.text)
            elif self.text:
                self.line2.setText(self.text)
        if self.rad2.isChecked():
            if self.text and self.index:
                if self.text.endswith(self.index):
                    self.text = ', '.join(self.text.split(', ')[:-1])
                    self.line2.setText(self.text)
            elif self.text:
                self.line2.setText(self.text)

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

    def waste(self):
        self.map_params.pop('pt')
        self.picture = change_picture(self.map_params)
        self.line2.setText('')
        self.text = ''
        self.index = ''
        self.draw()

    def draw(self):
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 600, 450)
        self.view.setScene(self.scene)
        self.scene.addItem(QGraphicsPixmapItem(self.picture))

    def searching(self):
        name = self.line.text()
        geocoder_params = {"geocode": name, "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params)
        if not response:
            return None

        json_response = response.json()
        radio = self.rad1.isChecked()
        self.map_params, address, index = \
            get_params(json_response, self.map_params['l'],
                       self.map_params['z'], radio=True,
                       booly=True)
        if radio and index:
            address += ', {}'.format(index)
        self.index = index
        self.text = address
        self.line2.setText(address)
        self.picture = change_picture(self.map_params)
        self.draw()

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        x -= 20
        y -= 10
        if 0 <= x <= 600 and 0 <= y <= 450:
            mid_x, mid_y = 295, 200
            x2, y2 = map(float, self.map_params['ll'].split(','))
            x = x2 - ((mid_x - x) * 360 / (2 ** (self.map_params['z'] + 8)))
            y = y2 + \
                (mid_y - y + 30) * 220 / (2 ** (self.map_params['z'] + 8))
            if event.button() == Qt.LeftButton:
                map_params2 = {'geocode': '{},{}'.format(x, y),
                               'format': 'json'}
                self.text, self.index = get_name(map_params2)
                self.indexing()
                self.map_params['pt'] = '{},{},pm2vvm'.format(x, y)
                self.picture = change_picture(self.map_params)
                self.draw()
            elif event.button() == Qt.RightButton:
                geocode_params = {'geocode': '{},{}'.format(x, y),
                                  'lang': 'ru_RU',
                                  'apikey': api_key,
                                  'type': 'biz'}
        else:
            return None

    def keyReleaseEvent(self, event):
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
