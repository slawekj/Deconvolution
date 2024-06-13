import os
import uuid
from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.uic import loadUi
from jproperties import Properties

from src.deconvolution import Deconvolver


class GuiQt(QMainWindow):
    def __init__(self):
        super(GuiQt, self).__init__()
        loadUi("../etc/Deconvolver.ui", self)

        self.deconvolver = Deconvolver()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.default_properties_file = os.path.join(dir_path, "..", "etc", "default.properties")
        self.default_signal_files = os.path.join(dir_path, "..", "etc", "files.txt")

        self.button_select_files.clicked.connect(self.select_files)
        self.button_clear_selection.clicked.connect(self.clear_selection)
        self.button_open.clicked.connect(self.open)
        self.button_save.clicked.connect(self.save)
        self.button_start.clicked.connect(self.start_pause_resume)

        self.experiment_uuid = None
        self.experiment_label = None
        self.experiment_checkpoint = None
        self.reset_experiment()

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

    def save_default_properties(self):
        with open(self.default_properties_file, "w") as file:
            file.write(self.text_fitting_model_properties.toPlainText())

    def load_default_signal_files(self):
        with open(self.default_signal_files, "r") as file:
            for line in file.readlines():
                self.text_signal_files.append(line.strip())

    def clear_files(self):
        self.text_signal_files.setText("")

    def save_signal_files(self):
        with open(self.default_signal_files, "w") as file:
            file.write(self.text_signal_files.toPlainText())

    def extract_file_names(self):
        filenames = []
        for line in self.text_signal_files.toPlainText().split("\n"):
            stripped_line = line.strip()
            if len(stripped_line) > 0:
                filenames.append(stripped_line)
        return filenames

    def extract_properties(self):
        properties = Properties()
        properties.load(self.text_fitting_model_properties.toPlainText())
        return properties.properties

    def on_closing(self):
        self.save_default_properties()
        self.save_signal_files()
        self.destroy()

    def reset_experiment(self):
        self.label_progress.setText("Progress:")
        self.text_progress.setText("")
        self.text_progress.setText("Press \"Start\" to begin...")
        self.progress_bar.reset()
        self.progress_bar.setValue(0)
        self.experiment_uuid = None
        self.experiment_label = None
        self.experiment_checkpoint = None
        self.button_start.setText("Start")

    def start_experiment(self, experiment_label, experiment_uuid):
        self.label_progress.setText("Progress: 0.00%")
        self.text_progress.setText("")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.experiment_uuid = experiment_uuid
        self.experiment_label = experiment_label
        # self.experiment_checkpoint unchanged
        self.button_start.setText("Pause")

    def resume_experiment(self, experiment_label, experiment_uuid):
        self.progress_bar.start()
        self.experiment_uuid = experiment_uuid
        self.experiment_label = experiment_label
        # self.experiment_checkpoint unchanged
        self.button_start.setText("Pause")

    def pause_experiment(self):
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.experiment_uuid = None
        self.button_start.setText("Resume")

    def finish_experiment(self):
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.experiment_uuid = None
        self.experiment_label = None
        self.experiment_checkpoint = None
        self.button_start.setText("Start")

    def is_experiment_current(self, experiment_uuid):
        return self.experiment_uuid == experiment_uuid

    def log_info_progress_line(self, progress_line):
        self.text_progress.append("[{ts}] INFO ".format(ts=datetime.now().strftime("%H:%M:%S")))
        # TODO add colors
        # current_text_length = len(self.text_progress.get("1.0", ctk.END))
        # self.text_progress.tag_add("blue_letters",
        #                            f"1.0 + {current_text_length - 6} chars",
        #                            f"1.0 + {current_text_length - 2} chars")
        # self.text_progress.tag_config("blue_letters", foreground="blue")
        self.text_progress.append("{progress_line}".format(progress_line=progress_line))

    def log_ok_progress_line(self, progress_line):
        self.text_progress.append("[{ts}] OK ".format(ts=datetime.now().strftime("%H:%M:%S")))
        # TODO add colors
        # current_text_length = len(self.text_progress.get("1.0", ctk.END))
        # self.text_progress.tag_add("green_letters",
        #                            f"1.0 + {current_text_length - 4} chars",
        #                            f"1.0 + {current_text_length - 2} chars")
        # self.text_progress.tag_config("green_letters", foreground="green")
        self.text_progress.append("{progress_line}".format(progress_line=progress_line))

    def log_error_progress_line(self, progress_line):
        self.text_progress.append("[{ts}] ERROR ".format(ts=datetime.now().strftime("%H:%M:%S")))
        # TODO add colors
        # current_text_length = len(self.text_progress.get("1.0", ctk.END))
        # self.text_progress.tag_add("red_letters",
        #                            f"1.0 + {current_text_length - 7} chars",
        #                            f"1.0 + {current_text_length - 2} chars")
        # self.text_progress.tag_config("red_letters", foreground="red")
        self.text_progress.append("{progress_line}".format(progress_line=progress_line))

    def run(self, experiment_label, experiment_uuid, filenames, first_index, last_index):
        properties = self.extract_properties()
        for i in range(first_index, last_index):
            if self.is_experiment_current(experiment_uuid):
                filename = filenames[i]
                deconvolution_status = self.deconvolver.deconvolve_single_file(
                    signal_file_abs_path=filename,
                    experiment_label=experiment_label,
                    properties=properties)
                if self.is_experiment_current(experiment_uuid):
                    if deconvolution_status.get("exit_code") == 0:
                        self.log_ok_progress_line("{filename}".format(
                            filename=filename
                        ))
                    else:
                        self.log_error_progress_line("{filename}".format(
                            filename=filename
                        ))
                        self.log_info_progress_line(
                            deconvolution_status.get("error_message").strip())
                    self.label_progress.setText(f"Progress: {round((i + 1) / len(filenames) * 100, 2)}%")
                    self.experiment_checkpoint = filename
        if self.is_experiment_current(experiment_uuid):
            self.log_info_progress_line(
                "{exp} finished".format(exp=experiment_label))
            self.finish_experiment()

    def start_pause_resume(self):
        if self.experiment_uuid is None and self.experiment_label is None:
            experiment_label = datetime.now().strftime("experiment_%m_%d_%Y__%H_%M_%S")
            experiment_uuid = str(uuid.uuid4())
            self.start_experiment(experiment_label, experiment_uuid)
            filenames = self.extract_file_names()
            if len(filenames) > 0:
                self.log_info_progress_line(
                    "{exp} started".format(exp=experiment_label))
                self.run(filenames=filenames,
                         experiment_label=experiment_label,
                         experiment_uuid=experiment_uuid,
                         first_index=0,
                         last_index=len(filenames))
            else:
                self.log_info_progress_line("No signal file(s) selected!")
                self.finish_experiment()
        elif self.experiment_uuid is None and self.experiment_label is not None:
            experiment_label = self.experiment_label
            experiment_uuid = str(uuid.uuid4())
            self.resume_experiment(experiment_label, experiment_uuid)
            self.log_info_progress_line(
                "{exp} resumed".format(exp=experiment_label))
            filenames = self.extract_file_names()
            if len(filenames) > 0:
                first_index = 1
                if self.experiment_checkpoint is not None:
                    first_index = filenames.index(
                        self.experiment_checkpoint) + 1
                self.run(filenames=filenames,
                         experiment_label=experiment_label,
                         experiment_uuid=experiment_uuid,
                         first_index=first_index,
                         last_index=len(filenames))
            else:
                self.log_info_progress_line("No signal file(s) selected!")
                self.finish_experiment()
        else:
            self.pause_experiment()
            self.log_info_progress_line(
                "{exp} paused".format(exp=self.experiment_label))

    def reset(self):
        self.reset_experiment()
