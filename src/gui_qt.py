import os
import uuid
from datetime import datetime

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QRunnable, QThreadPool
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.uic import loadUi
from jproperties import Properties

from src.deconvolution import Deconvolver


class Signals(QObject):
    reset_text_progress = pyqtSignal(str)
    update_text_progress = pyqtSignal(str)


class AsyncExecution(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(AsyncExecution, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = Signals()

    @pyqtSlot()
    def run(self):
        self.fn(self.signals, *self.args, **self.kwargs)


class GuiQt(QMainWindow):
    def __init__(self):
        super(GuiQt, self).__init__()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        loadUi(os.path.join(dir_path, "..", "etc", "Deconvolver.ui"), self)

        self.default_properties_file = os.path.join(dir_path, "..", "etc", "default.properties")
        self.default_signal_files = os.path.join(dir_path, "..", "etc", "files.txt")
        self.load_signal_files(self.default_signal_files)
        self.load_properties(self.default_properties_file)

        # main event loop
        self.button_select_files.clicked.connect(self.select_files)
        self.button_clear_selection.clicked.connect(self.clear_selection)
        self.button_open.clicked.connect(self.open)
        self.button_save.clicked.connect(self.save)
        self.button_reset.clicked.connect(self.reset_experiment)

        # async event loop
        self.threadpool = QThreadPool()
        self.button_start.clicked.connect(self.async_start_pause_resume)

        self.deconvolver = Deconvolver()
        self.experiment_uuid = None
        self.experiment_label = None
        self.experiment_checkpoint = None
        self.reset_experiment()

    def closeEvent(self, event):
        self.save_default_properties()
        self.save_default_signal_files()
        super().closeEvent(event)

    def async_start_pause_resume(self):
        execution = AsyncExecution(self.start_pause_resume)
        execution.signals.update_text_progress.connect(self.log_progress_line)
        execution.signals.reset_text_progress.connect(self.reset_progress_line)
        self.threadpool.start(execution)

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

    def load_signal_files(self, signal_files):
        with open(signal_files, "r") as file:
            for line in file.readlines():
                self.text_signal_files.append(line.strip())

    def clear_files(self):
        self.text_signal_files.setText("")

    def save_default_signal_files(self):
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

    def reset_experiment(self, signal_text_progress_reset=None):
        self.label_progress.setText("Progress:")
        if signal_text_progress_reset:
            signal_text_progress_reset.emit("Press \"Start\" to begin...")
        else:
            self.text_progress.setText("")
            self.text_progress.setText("Press \"Start\" to begin...")
        self.progress_bar.reset()
        self.progress_bar.setValue(0)
        self.experiment_uuid = None
        self.experiment_label = None
        self.experiment_checkpoint = None
        self.button_start.setText("Start")

    def start_experiment(self, experiment_label, experiment_uuid, signal_text_progress_reset=None):
        self.label_progress.setText("Progress: 0.00%")
        if signal_text_progress_reset:
            signal_text_progress_reset.emit("")
        else:
            self.text_progress.setText("")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.experiment_uuid = experiment_uuid
        self.experiment_label = experiment_label
        # self.experiment_checkpoint unchanged
        self.button_start.setText("Pause")

    def resume_experiment(self, experiment_label, experiment_uuid):
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
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

    def log_progress_line(self, progress_line):
        # TODO add colors
        self.text_progress.append("[{ts}] INFO {progress_line}".format(
            ts=datetime.now().strftime("%H:%M:%S"),
            progress_line=progress_line
        ))

    def reset_progress_line(self, progress_line):
        self.text_progress.setText(progress_line)

    def run(self, signals, experiment_label, experiment_uuid, filenames, first_index, last_index):
        properties = self.extract_properties()
        for i in range(first_index, last_index):
            if self.is_experiment_current(experiment_uuid):
                filename = filenames[i]
                deconvolution_status = self.deconvolver.deconvolve_single_file(
                    signal_file_abs_path=filename,
                    experiment_label=experiment_label,
                    properties=properties,
                    plot_peaks=False)
                if self.is_experiment_current(experiment_uuid):
                    if deconvolution_status.get("exit_code") == 0:
                        signals.update_text_progress.emit("{filename}".format(filename=filename))
                    else:
                        # TODO log as error
                        signals.update_text_progress.emit("{filename}".format(filename=filename))
                        signals.update_text_progress.emit(deconvolution_status.get("error_message").strip())
                    self.label_progress.setText(f"Progress: {round((i + 1) / len(filenames) * 100, 2)}%")
                    self.experiment_checkpoint = filename
        if self.is_experiment_current(experiment_uuid):
            signals.update_text_progress.emit("{exp} finished".format(exp=experiment_label))
            self.finish_experiment()

    def start_pause_resume(self, signals):
        if self.experiment_uuid is None and self.experiment_label is None:
            experiment_label = datetime.now().strftime("experiment_%m_%d_%Y__%H_%M_%S")
            experiment_uuid = str(uuid.uuid4())
            self.start_experiment(experiment_label, experiment_uuid, signals.reset_text_progress)
            filenames = self.extract_file_names()
            if len(filenames) > 0:
                signals.update_text_progress.emit("{exp} started".format(exp=experiment_label))
                self.run(
                    signals=signals,
                    filenames=filenames,
                    experiment_label=experiment_label,
                    experiment_uuid=experiment_uuid,
                    first_index=0,
                    last_index=len(filenames))
            else:
                signals.update_text_progress.emit("No signal file(s) selected!")
                self.finish_experiment()
        elif self.experiment_uuid is None and self.experiment_label is not None:
            experiment_label = self.experiment_label
            experiment_uuid = str(uuid.uuid4())
            self.resume_experiment(experiment_label, experiment_uuid)
            signals.update_text_progress.emit("{exp} resumed".format(exp=experiment_label))
            filenames = self.extract_file_names()
            if len(filenames) > 0:
                first_index = 1
                if self.experiment_checkpoint is not None:
                    first_index = filenames.index(self.experiment_checkpoint) + 1
                self.run(
                    signals=signals,
                    filenames=filenames,
                    experiment_label=experiment_label,
                    experiment_uuid=experiment_uuid,
                    first_index=first_index,
                    last_index=len(filenames))
            else:
                signals.update_text_progress.emit("No signal file(s) selected!")
                self.finish_experiment()
        else:
            self.pause_experiment()
            signals.update_text_progress.emit("{exp} paused".format(exp=self.experiment_label))
