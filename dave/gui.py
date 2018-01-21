from PyQt5 import QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import QUrl


def main():
    # Create application
    app = QtWidgets.QApplication([])

    # Add a window
    win = QtWidgets.QWidget()
    win.setWindowTitle('DAVE')

    # Create a layout
    layout = QtWidgets.QVBoxLayout()
    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)

    win.setLayout(layout)
    win.resize(450, 700)

    # Add a QWebEngineView
    view = QtWebEngineWidgets.QWebEngineView()
    view.setUrl(QUrl("http://localhost:5128/"))

    # Add the web view to the layout
    layout.addWidget(view)

    # Run the app
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()
