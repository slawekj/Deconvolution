import json
import os
import os.path as path_utils
import pathlib
import uuid
from datetime import datetime
from threading import Thread
from tkinter import filedialog as fd

import customtkinter as ctk
from click.testing import CliRunner
from jproperties import Properties

from src.logic.ellipses import extrapolate_ellipse
from src.ui.progress_textbox import ProgressTextbox


class EllipsesTab:
    def __init__(self, tab: ctk.CTkFrame):
        self.tab = tab
        self.diameter_files = {"long diameter": "N/A", "short diameter": "N/A"}

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.default_properties_file = os.path.join(
            dir_path, "..", "..", "etc", "ellipses", "default.properties")
        self.default_signal_files = os.path.join(
            dir_path, "..", "..", "etc", "ellipses", "files.txt")

        self.tab.grid_columnconfigure(0, weight=1)
        self.tab.grid_columnconfigure(1, weight=1)
        self.tab.grid_columnconfigure(2, weight=1)
        self.tab.grid_rowconfigure(0, weight=1)

        self.signal_selection_frame = ctk.CTkFrame(master=self.tab)
        self.signal_selection_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.model_selection_frame = ctk.CTkFrame(master=self.tab)
        self.model_selection_frame.grid(
            row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.progress_frame = ctk.CTkFrame(master=self.tab)
        self.progress_frame.grid(
            row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.model_selection_label = ctk.CTkLabel(
            master=self.signal_selection_frame, text="Diagonal files:")
        self.model_selection_label.pack(pady=12, padx=10)

        self.signal_files_textbox = ctk.CTkTextbox(master=self.signal_selection_frame, wrap="none",
                                                   font=ctk.CTkFont(family="Courier"))
        self.signal_files_textbox.pack(
            pady=12, padx=10, expand=True, fill="both")
        self.load_default_signal_files()

        self.select_long_diameter_file_button = ctk.CTkButton(master=self.signal_selection_frame,
                                                              text="Long diameter file...",
                                                              command=lambda: Thread(
                                                                  target=self.select_diameter_file,
                                                                  args=["long diameter"]).start())
        self.select_long_diameter_file_button.pack(pady=12, padx=10)

        self.select_short_diameter_file_button = ctk.CTkButton(master=self.signal_selection_frame,
                                                               text="Short diameter file...",
                                                               command=lambda: Thread(
                                                                   target=self.select_diameter_file,
                                                                   args=["short diameter"]).start())
        self.select_short_diameter_file_button.pack(pady=12, padx=10)

        self.clear_selection_button = ctk.CTkButton(master=self.signal_selection_frame,
                                                    text="Clear selection",
                                                    command=lambda: Thread(target=self.clear_files).start())
        self.clear_selection_button.pack(pady=12, padx=10)

        self.model_selection_label = ctk.CTkLabel(master=self.model_selection_frame,
                                                  text="Extrapolation model properties:")
        self.model_selection_label.pack(pady=12, padx=10)

        self.model_selection_textbox = ctk.CTkTextbox(master=self.model_selection_frame, wrap="none",
                                                      font=ctk.CTkFont(family="Courier"))
        self.model_selection_textbox.pack(
            pady=12, padx=10, expand=True, fill="both")
        self.load_properties(self.default_properties_file)

        self.model_open_button = ctk.CTkButton(master=self.model_selection_frame,
                                               text="Open...",
                                               command=lambda: Thread(target=self.select_properties_file).start())
        self.model_open_button.pack(pady=12, padx=10)

        self.model_save_button = ctk.CTkButton(master=self.model_selection_frame,
                                               text="Save...",
                                               command=lambda: Thread(target=self.save_properties).start())
        self.model_save_button.pack(pady=12, padx=10)

        self.progress_label = ctk.CTkLabel(
            master=self.progress_frame, text="Progress:")
        self.progress_label.pack(pady=12, padx=10)

        self.progress_textbox = ProgressTextbox(master=self.progress_frame, wrap="none",
                                                font=ctk.CTkFont(family="Courier"))
        self.progress_textbox.pack(pady=12, padx=10, expand=True, fill="both")

        self.start_button = ctk.CTkButton(master=self.progress_frame, text="Run",
                                          command=lambda: Thread(target=self.start).start())
        self.start_button.pack(pady=12, padx=10)

        self.experiment_uuid = None
        self.experiment_label = None
        self.reset_experiment()

    def select_diameter_file(self, label):
        filetypes = (
            ("Text files", "*.tsv"),
            ("All files", "*.*")
        )
        filename = fd.askopenfilename(
            title="Open file",
            initialdir="",
            filetypes=filetypes)
        if filename is not None:
            self.signal_files_textbox.delete("1.0", ctk.END)
            self.diameter_files[label] = filename
            self.signal_files_textbox.insert(ctk.END, json.dumps(self.diameter_files, indent=4))

    def load_default_signal_files(self):
        with open(self.default_signal_files, "r") as file:
            for line in file.readlines():
                self.signal_files_textbox.insert(ctk.END, line)
            tmp = json.loads(self.signal_files_textbox.get("1.0", ctk.END))
            self.diameter_files["long diameter"] = tmp["long diameter"]
            self.diameter_files["short diameter"] = tmp["short diameter"]

    def clear_files(self):
        self.signal_files_textbox.delete(1.0, ctk.END)
        self.diameter_files["long diameter"] = "N/A"
        self.diameter_files["short diameter"] = "N/A"
        self.signal_files_textbox.insert(ctk.END, json.dumps(self.diameter_files, indent=4))

    def save_signal_files(self):
        with open(self.default_signal_files, "w") as file:
            file.write(self.signal_files_textbox.get("1.0", ctk.END).strip())

    def load_properties(self, file_path):
        with open(file_path, "r") as file:
            self.model_selection_textbox.delete(1.0, ctk.END)
            for line in file.readlines():
                self.model_selection_textbox.insert(ctk.END, line)

    def save_default_properties(self):
        with open(self.default_properties_file, "w") as file:
            file.write(self.model_selection_textbox.get(
                "1.0", ctk.END).strip())

    def select_properties_file(self):
        filetypes = (
            ("Text files", "*.properties"),
            ("All files", "*.*")
        )
        filename = fd.askopenfilename(
            title="Open file",
            initialdir=pathlib.Path.home(),
            filetypes=filetypes
        )
        if len(filename) > 0:
            self.load_properties(filename)

    def save_properties(self):
        filetypes = (
            ("Property file", "*.properties"),
            ("All files", "*.*")
        )
        file = fd.asksaveasfile(title="Save property file",
                                initialdir=pathlib.Path.home(),
                                filetypes=filetypes)
        if file is not None:
            with file:
                file.write(self.model_selection_textbox.get(
                    "1.0", ctk.END).strip())

    def start(self):
        try:
            if self.experiment_uuid is None and self.experiment_label is None:
                experiment_label = datetime.now().strftime("experiment_%m_%d_%Y__%H_%M_%S")
                experiment_uuid = str(uuid.uuid4())
                self.start_experiment(experiment_label, experiment_uuid)
                self.progress_textbox.log_info_progress_line("{exp} started".format(exp=experiment_label))

                # Prepare experiment
                if self.diameter_files["long diameter"] == "N/A":
                    raise Exception("Long diameter file not selected")

                if self.diameter_files["short diameter"] == "N/A":
                    raise Exception("Short diameter file not selected")

                long_diameter_file_directory = path_utils.dirname(self.diameter_files["long diameter"])
                output_dir = path_utils.join(long_diameter_file_directory, experiment_label)
                path_utils.exists(output_dir) or os.mkdir(output_dir)
                properties = self.extract_properties()
                output_file_name = properties["output_file_name"]

                # Run experiment
                runner = CliRunner()
                result = runner.invoke(extrapolate_ellipse, [
                    '--long-diameter-file', self.diameter_files["long diameter"],
                    '--short-diameter-file', self.diameter_files["short diameter"],
                    '--output-file', path_utils.join(output_dir, output_file_name),
                    '--skip-plotting-results'
                ])

                # Report experiment
                if result.exit_code == 0:
                    self.progress_textbox.log_info_progress_line("{exp} finished".format(exp=experiment_label))
                    self.progress_textbox.log_info_progress_line("results:\n" + result.stdout)
                    self.progress_textbox.log_experiment_hyperlink_line(output_dir)
                else:
                    self.progress_textbox.log_error_progress_line("\n" + result.stdout)
                self.finish_experiment()
        except Exception as e:
            self.progress_textbox.log_error_progress_line(str(e))
            self.finish_experiment()

    def extract_properties(self):
        properties = Properties()
        properties.load(self.model_selection_textbox.get("1.0", ctk.END))
        return properties.properties

    def on_closing(self):
        self.save_default_properties()
        self.save_signal_files()

    def reset_experiment(self):
        self.progress_textbox.delete(1.0, ctk.END)
        self.progress_textbox.insert(ctk.END, "Press \"Run\" to begin...")
        self.experiment_uuid = None
        self.experiment_label = None
        self.start_button.configure(state=ctk.NORMAL)

    def start_experiment(self, experiment_label, experiment_uuid):
        self.progress_textbox.delete(1.0, ctk.END)
        self.experiment_uuid = experiment_uuid
        self.experiment_label = experiment_label
        # self.experiment_checkpoint unchanged
        self.start_button.configure(state=ctk.DISABLED)

    def finish_experiment(self):
        self.experiment_uuid = None
        self.experiment_label = None
        self.start_button.configure(state=ctk.NORMAL)

    def is_experiment_current(self, experiment_uuid):
        return self.experiment_uuid == experiment_uuid
