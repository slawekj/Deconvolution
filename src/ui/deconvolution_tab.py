import os
import uuid
from datetime import datetime
from threading import Thread
from tkinter import filedialog as fd

import customtkinter as ctk

from src.logic.deconvolution import Deconvolver
from src.ui.progress_textbox import ProgressTextbox
from src.ui.properties_frame import PropertiesFrame


class DeconvolutionTab:
    def __init__(self, frame: ctk.CTkFrame):
        self.frame = frame
        self.deconvolver = Deconvolver()

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.default_properties_file = os.path.join(
            dir_path, "..", "..", "etc", "deconvolution", "default.properties")
        self.default_signal_files = os.path.join(
            dir_path, "..", "..", "etc", "deconvolution", "files.txt")

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        self.signal_selection_frame = ctk.CTkFrame(master=self.frame)
        self.signal_selection_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.model_selection_frame = PropertiesFrame(master=self.frame,
                                                     default_properties_file=self.default_properties_file,
                                                     label="Fitting model properties:")
        self.model_selection_frame.grid(
            row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.progress_frame = ctk.CTkFrame(master=self.frame)
        self.progress_frame.grid(
            row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.model_selection_label = ctk.CTkLabel(
            master=self.signal_selection_frame, text="Signal file(s):")
        self.model_selection_label.pack(pady=12, padx=10)

        self.signal_files_textbox = ctk.CTkTextbox(master=self.signal_selection_frame, wrap="none",
                                                   font=ctk.CTkFont(family="Courier"))
        self.signal_files_textbox.pack(
            pady=12, padx=10, expand=True, fill="both")
        self.load_default_signal_files()

        self.select_signal_files_button = ctk.CTkButton(master=self.signal_selection_frame,
                                                        text="Select file(s)...",
                                                        command=lambda: Thread(target=self.select_signal_files).start())
        self.select_signal_files_button.pack(pady=12, padx=10)

        self.clear_selection_button = ctk.CTkButton(master=self.signal_selection_frame,
                                                    text="Clear selection",
                                                    command=lambda: Thread(target=self.clear_files).start())
        self.clear_selection_button.pack(pady=12, padx=10)

        self.progress_label = ctk.CTkLabel(
            master=self.progress_frame, text="Progress:")
        self.progress_label.pack(pady=12, padx=10)

        self.progress_bar = ctk.CTkProgressBar(master=self.progress_frame, orientation="horizontal",
                                               mode="indeterminate")
        self.progress_bar.pack(pady=12, padx=10)
        self.progress_bar.set(0.0)

        self.progress_textbox = ProgressTextbox(master=self.progress_frame, wrap="none",
                                                font=ctk.CTkFont(family="Courier"))
        self.progress_textbox.pack(pady=12, padx=10, expand=True, fill="both")

        self.start_button = ctk.CTkButton(master=self.progress_frame, text="Start",
                                          command=lambda: Thread(target=self.start_pause_resume).start())
        self.start_button.pack(pady=12, padx=10)

        self.reset_button = ctk.CTkButton(master=self.progress_frame, text="Reset",
                                          command=lambda: Thread(target=self.reset_experiment).start())
        self.reset_button.pack(pady=12, padx=10)

        self.experiment_uuid = None
        self.experiment_label = None
        self.experiment_checkpoint = None
        self.reset_experiment()

    def load_default_signal_files(self):
        with open(self.default_signal_files, "r") as file:
            for line in file.readlines():
                self.signal_files_textbox.insert(ctk.END, line)

    def clear_files(self):
        self.signal_files_textbox.delete(1.0, ctk.END)

    def save_signal_files(self):
        with open(self.default_signal_files, "w") as file:
            file.write(self.signal_files_textbox.get("1.0", ctk.END).strip())

    def select_signal_files(self):
        filetypes = (
            ("Text files", "*.dpt"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        )
        filenames = fd.askopenfilenames(
            title="Open file(s)",
            initialdir="",
            filetypes=filetypes)
        if len(filenames) > 0:
            self.signal_files_textbox.delete("1.0", ctk.END)
        for filename in filenames:
            self.signal_files_textbox.insert(ctk.END, filename + "\n")

    def extract_file_names(self):
        filenames = []
        for line in self.signal_files_textbox.get("1.0", ctk.END).split("\n"):
            stripped_line = line.strip()
            if len(stripped_line) > 0:
                filenames.append(stripped_line)
        return filenames

    def on_closing(self):
        self.model_selection_frame.save_default_properties()
        self.save_signal_files()

    def reset_experiment(self):
        self.progress_label.configure(text="Progress:")
        self.progress_textbox.delete(1.0, ctk.END)
        self.progress_textbox.insert(ctk.END, "Press \"Start\" to begin...")
        self.progress_bar.stop()
        self.progress_bar.set(0.0)
        self.experiment_uuid = None
        self.experiment_label = None
        self.experiment_checkpoint = None
        self.start_button.configure(text="Start")

    def start_experiment(self, experiment_label, experiment_uuid):
        self.progress_label.configure(text="Progress: 0.00%")
        self.progress_textbox.delete(1.0, ctk.END)
        self.progress_bar.start()
        self.experiment_uuid = experiment_uuid
        self.experiment_label = experiment_label
        # self.experiment_checkpoint unchanged
        self.start_button.configure(text="Pause")

    def resume_experiment(self, experiment_label, experiment_uuid):
        self.progress_bar.start()
        self.experiment_uuid = experiment_uuid
        self.experiment_label = experiment_label
        # self.experiment_checkpoint unchanged
        self.start_button.configure(text="Pause")

    def pause_experiment(self):
        self.progress_bar.stop()
        self.experiment_uuid = None
        self.start_button.configure(text="Resume")

    def finish_experiment(self):
        self.progress_bar.stop()
        self.experiment_uuid = None
        self.experiment_label = None
        self.experiment_checkpoint = None
        self.start_button.configure(text="Start")

    def is_experiment_current(self, experiment_uuid):
        return self.experiment_uuid == experiment_uuid

    def run(self, experiment_label, experiment_uuid, filenames, first_index, last_index):
        properties = self.model_selection_frame.extract_properties()
        deconvolution_status = None
        for i in range(first_index, last_index):
            if self.is_experiment_current(experiment_uuid):
                filename = filenames[i]
                deconvolution_status = self.deconvolver.deconvolve_single_file(
                    signal_file_abs_path=filename,
                    experiment_label=experiment_label,
                    properties=properties)
                if self.is_experiment_current(experiment_uuid):
                    if deconvolution_status.get("exit_code") == 0:
                        self.progress_textbox.log_ok_progress_line("{filename}".format(
                            filename=filename
                        ))
                    else:
                        self.progress_textbox.log_error_progress_line("{filename}".format(
                            filename=filename
                        ))
                        self.progress_textbox.log_info_progress_line(
                            deconvolution_status.get("error_message").strip())
                    self.progress_label.configure(
                        text=f"Progress: {round((i + 1) / len(filenames) * 100, 2)}%")
                    self.experiment_checkpoint = i
        if self.is_experiment_current(experiment_uuid):
            self.progress_textbox.log_info_progress_line("{exp} finished".format(exp=experiment_label))
            if deconvolution_status is not None:
                self.progress_textbox.log_experiment_hyperlink_line(deconvolution_status.get("output_dir"))
            self.finish_experiment()

    def start_pause_resume(self):
        if self.experiment_uuid is None and self.experiment_label is None:
            experiment_label = datetime.now().strftime("experiment_%m_%d_%Y__%H_%M_%S")
            experiment_uuid = str(uuid.uuid4())
            self.start_experiment(experiment_label, experiment_uuid)
            filenames = self.extract_file_names()
            if len(filenames) > 0:
                self.progress_textbox.log_info_progress_line("{exp} started".format(exp=experiment_label))
                self.run(filenames=filenames,
                         experiment_label=experiment_label,
                         experiment_uuid=experiment_uuid,
                         first_index=0,
                         last_index=len(filenames))
            else:
                self.progress_textbox.log_info_progress_line("No signal file(s) selected!")
                self.finish_experiment()
        elif self.experiment_uuid is None and self.experiment_label is not None:
            experiment_label = self.experiment_label
            experiment_uuid = str(uuid.uuid4())
            self.resume_experiment(experiment_label, experiment_uuid)
            self.progress_textbox.log_info_progress_line(
                "{exp} resumed".format(exp=experiment_label))
            filenames = self.extract_file_names()
            if len(filenames) > 0:
                first_index = 1
                if self.experiment_checkpoint is not None:
                    first_index = self.experiment_checkpoint + 1
                self.run(filenames=filenames,
                         experiment_label=experiment_label,
                         experiment_uuid=experiment_uuid,
                         first_index=first_index,
                         last_index=len(filenames))
            else:
                self.progress_textbox.log_info_progress_line("No signal file(s) selected!")
                self.finish_experiment()
        else:
            self.pause_experiment()
            self.progress_textbox.log_info_progress_line(
                "{exp} paused".format(exp=self.experiment_label))
