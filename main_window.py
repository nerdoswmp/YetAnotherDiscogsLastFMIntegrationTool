import urllib.request

import requests
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLineEdit, QGridLayout, QScrollArea, QWidget, QLabel, \
    QApplication
from discogs_client import Client, Release


class ImageWindow(QWidget):
    def __init__(self, parent, url, text):
        super().__init__(parent)
        self.setMaximumSize(200, 200)

        self.layout = QVBoxLayout(self)
        self.label = QLabel("Loading image...")
        self.layout.addWidget(self.label)
        text_label = QLabel(text)

        self.layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Download and set image
        self.set_image_from_url(url)

    def set_image_from_url(self, url):
        app = QApplication.instance()

        headers = {
            "User-Agent": app.name
        }
        try:
            response = requests.get(url, stream=True, headers=headers)
            pixmap = QPixmap()

            pixmap.loadFromData(response.content)

            self.label.setPixmap(pixmap)
            self.label.setScaledContents(True)
        except Exception as e:
            self.label.setText(f"Failed to load image: {e}")


class ScrollGrid(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)

        layout = QVBoxLayout(self)

        wrapper = QWidget()
        self._grid = QGridLayout(wrapper)
        wrapper.setLayout(self._grid)

        scroll = QScrollArea(self)
        scroll.setWidget(wrapper)
        scroll.setWidgetResizable(True)

        layout.addWidget(scroll)

    def addWidget(self, widget, row, col):
        self._grid.addWidget(widget, row, col)


class SearchPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.max_h = 5

        self.debounce_timer = QTimer(self, interval=1000)
        self.debounce_timer.setSingleShot(True)

        layout = QVBoxLayout(self)

        release_input = QLineEdit(self)
        release_input.textChanged.connect(self.trigger_search)

        layout.addWidget(release_input)

        self.debounce_timer.timeout.connect(lambda: self.search_releases(release_input.text()))

        g = ScrollGrid(self)

        layout.addWidget(g)

    def trigger_search(self):
        self.debounce_timer.stop()

        self.debounce_timer.start()

    def search_releases(self, search_query):
        layout: QVBoxLayout = self.layout()

        layout.itemAt(1).widget().deleteLater()

        grid = ScrollGrid(self)

        app = QApplication.instance()

        discogs: Client = app.client

        results = discogs.search(search_query, type="release")

        row = 0
        col = 0
        for release in results.page(1):
            release: Release = release
            print(release.title, row, col)
            try:
                image = release.images[0]["resource_url"]
            except IndexError:
                image = r"https://m.media-amazon.com/images/I/519Hct2QoeL._AC_UF894,1000_QL80_.jpg"

            w = ImageWindow(self, image, release.title)

            grid.addWidget(w, row, col)

            col += 1

            if col == self.max_h:
                row += 1
                col = 0

        layout.insertWidget(1, grid)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(1024, 768)

        search_page = SearchPage(self)

        self.setCentralWidget(search_page)
