from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.uic import loadUi


class GuiQt(QMainWindow):
    def __init__(self):
        super(GuiQt, self).__init__()
        loadUi("../etc/Deconvolver.ui", self)

        self.button_select_files.clicked.connect(self.select_files)
        self.button_clear_selection.clicked.connect(self.clear_selection)
        self.button_open.clicked.connect(self.open)
        self.button_save.clicked.connect(self.save)

    def select_files(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, "Open file(s)", "",
                                                    "DPT Files (*.dpt);;Text Files (*.txt);;All Files (*)")
        if len(filenames) > 0:
            self.text_signal_files.setText("")
        for filename in filenames:
            self.text_signal_files.append(filename.strip())

    def clear_selection(self):
        self.text_signal_files.setText("")

    def open(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                  "Property Files (*.properties);;All Files (*)")
        if len(filename) > 0:
            self.load_properties(filename)

    def load_properties(self, file_path):
        with open(file_path, "r") as file:
            self.text_fitting_model_properties.setText("")
            for line in file:
                self.text_fitting_model_properties.append(line.strip())

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save file", "",
                                                  "Property Files (*.properties);;All Files (*))")
        if filename:
            with open(filename, "w") as file:
                file.write(self.text_fitting_model_properties.toPlainText())
