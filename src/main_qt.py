import sys

from PyQt5.QtWidgets import QApplication
from gui_qt import GuiQt

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = GuiQt(app)
    ui.show()
    app.exec_()
