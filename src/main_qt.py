import pathlib
from threading import Thread

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.uic import loadUi
import sys


class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        loadUi("../etc/Deconvolver.ui", self)

        self.button_select_files.clicked.connect(self.select_files)

    def select_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filenames, _ = QFileDialog.getOpenFileNames(self, "Open files(s)", "", "Text files (*.dpt, *.txt, *.*)",
                                                    options=options)
        if len(filenames) > 0:
            self.text_signal_files.setText("")
        for filename in filenames:
            self.text_signal_files.append(filename)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec_()
