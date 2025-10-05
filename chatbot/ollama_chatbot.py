import sys

from PyQt6.QtWidgets import QApplication

from chatbot.gui.gui import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


main()
