import sys

import discogs_client
from PySide6.QtWidgets import QApplication

from main_window import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.name = 'YetAnotherDiscogsLastFMIntegrationToolTest/0.1'

    app.client = discogs_client.Client(app.name)

    window = MainWindow()
    window.show()
    app.exec()


