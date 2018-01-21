from PyQt5 import QtWidgets


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

    # Run the app
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()
