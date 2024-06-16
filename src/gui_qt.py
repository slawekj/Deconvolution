import os
import uuid
from datetime import datetime

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QRunnable, QThreadPool
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.uic import loadUi
from jproperties import Properties

from deconvolution import Deconvolver


class Signals(QObject):
    reset_text_progress = pyqtSignal(str)
    update_text_progress = pyqtSignal(str)
    start_bar_progress = pyqtSignal()
    stop_bar_progress = pyqtSignal(int)


class AsyncProgressText:

    def __init__(self, text_widget, append_signal, reset_signal):
        self.text_widget = text_widget
        self.append_signal = append_signal
        self.reset_signal = reset_signal
        self.append_signal.connect(self.__append)
        self.reset_signal.connect(self.__reset)

    def append(self, text):
        self.append_signal.emit(text)

    def __append(self, text):
        self.text_widget.append(text)

    def reset(self, text):
        self.reset_signal.emit(text)

    def __reset(self, text):
        self.text_widget.setText(text)


class AsyncProgressBar:

    def __init__(self, progress_bar, start_signal, stop_signal):
        self.progress_bar = progress_bar
        self.start_signal = start_signal
        self.stop_signal = stop_signal
        self.start_signal.connect(self.__start)
        self.stop_signal.connect(self.__stop)

    def start(self):
        self.start_signal.emit()

    def __start(self):
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)

    def stop(self, value):
        self.stop_signal.emit(value)

    def __stop(self, value):
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(value)


class AsyncExecution(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(AsyncExecution, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)


class GuiQt(QMainWindow):
    def __init__(self):
        super(GuiQt, self).__init__()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        loadUi(os.path.join(dir_path, "..", "etc", "Deconvolver.ui"), self)

        self.default_properties_file = os.path.join(dir_path, "..", "etc", "default.properties")
        self.default_signal_files = os.path.join(dir_path, "..", "etc", "files.txt")
        self.load_signal_files(self.default_signal_files)
        self.load_properties(self.default_properties_file)

        self.main_thread_signals = Signals()
        self.thread_safe_progress_text = AsyncProgressText(self.text_progress,
                                                           self.main_thread_signals.update_text_progress,
                                                           self.main_thread_signals.reset_text_progress)

        self.thread_safe_progress_bar = AsyncProgressBar(self.progress_bar,
                                                         self.main_thread_signals.start_bar_progress,
                                                         self.main_thread_signals.stop_bar_progress)

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
        self.progress_percent = 0
        self.reset_experiment()

    def closeEvent(self, event):
        self.save_default_properties()
        self.save_default_signal_files()
        super().closeEvent(event)

    def async_start_pause_resume(self):
        execution = AsyncExecution(self.start_pause_resume)
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

    def reset_experiment(self):
        self.progress_percent = 0
        self.label_progress.setText("Progress:")
        self.thread_safe_progress_text.reset("Press \"Start\" to begin...")
        self.thread_safe_progress_bar.stop(0)
        self.experiment_uuid = None
        self.experiment_label = None
        self.experiment_checkpoint = None
        self.button_start.setText("Start")

    def start_experiment(self, experiment_label, experiment_uuid):
        self.progress_percent = 0
        self.label_progress.setText("Progress: 0.00%")
        self.thread_safe_progress_text.reset("")
        self.thread_safe_progress_bar.start()
        self.experiment_uuid = experiment_uuid
        self.experiment_label = experiment_label
        # self.experiment_checkpoint unchanged
        self.button_start.setText("Pause")

    def resume_experiment(self, experiment_label, experiment_uuid):
        self.thread_safe_progress_bar.start()
        self.experiment_uuid = experiment_uuid
        self.experiment_label = experiment_label
        # self.experiment_checkpoint unchanged
        self.button_start.setText("Pause")

    def pause_experiment(self):
        self.thread_safe_progress_bar.stop(int(self.progress_percent))
        self.experiment_uuid = None
        self.button_start.setText("Resume")

    def finish_experiment(self):
        self.thread_safe_progress_bar.stop(100)
        self.experiment_uuid = None
        self.experiment_label = None
        self.experiment_checkpoint = None
        self.button_start.setText("Start")

    def is_experiment_current(self, experiment_uuid):
        return self.experiment_uuid == experiment_uuid

    def log_progress_line(self, progress_line):
        # TODO add colors
        self.thread_safe_progress_text.append("[{ts}] INFO {progress_line}".format(
            ts=datetime.now().strftime("%H:%M:%S"),
            progress_line=progress_line
        ))

    def run(self, experiment_label, experiment_uuid, filenames, first_index, last_index):
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
                        self.thread_safe_progress_text.append("[{ts}] OK {filename}".format(
                            ts=datetime.now().strftime("%H:%M:%S"),
                            filename=filename
                        ))
                    else:
                        # TODO log as error
                        self.thread_safe_progress_text.append("[{ts}] ERROR {filename}".format(
                            ts=datetime.now().strftime("%H:%M:%S"),
                            filename=filename
                        ))
                        self.thread_safe_progress_text.append(deconvolution_status.get("error_message").strip())
                    self.progress_percent = round((i + 1) / len(filenames) * 100, 2)
                    self.label_progress.setText(f"Progress: {self.progress_percent}%")
                    self.experiment_checkpoint = filename
        if self.is_experiment_current(experiment_uuid):
            self.thread_safe_progress_text.append("{exp} finished".format(exp=experiment_label))
            self.finish_experiment()

    def start_pause_resume(self):
        if self.experiment_uuid is None and self.experiment_label is None:
            experiment_label = datetime.now().strftime("experiment_%m_%d_%Y__%H_%M_%S")
            experiment_uuid = str(uuid.uuid4())
            self.start_experiment(experiment_label, experiment_uuid)
            filenames = self.extract_file_names()
            if len(filenames) > 0:
                self.thread_safe_progress_text.append("{exp} started".format(exp=experiment_label))
                self.run(
                    filenames=filenames,
                    experiment_label=experiment_label,
                    experiment_uuid=experiment_uuid,
                    first_index=0,
                    last_index=len(filenames))
            else:
                self.thread_safe_progress_text.append("No signal file(s) selected!")
                self.finish_experiment()
        elif self.experiment_uuid is None and self.experiment_label is not None:
            experiment_label = self.experiment_label
            experiment_uuid = str(uuid.uuid4())
            self.resume_experiment(experiment_label, experiment_uuid)
            self.thread_safe_progress_text.append("{exp} resumed".format(exp=experiment_label))
            filenames = self.extract_file_names()
            if len(filenames) > 0:
                first_index = 1
                if self.experiment_checkpoint is not None:
                    first_index = filenames.index(self.experiment_checkpoint) + 1
                self.run(
                    filenames=filenames,
                    experiment_label=experiment_label,
                    experiment_uuid=experiment_uuid,
                    first_index=first_index,
                    last_index=len(filenames))
            else:
                self.thread_safe_progress_text.append("{exp} finished".format(exp=experiment_label))
                self.finish_experiment()
        else:
            self.pause_experiment()
            self.thread_safe_progress_text.append("{exp} paused".format(exp=self.experiment_label))
