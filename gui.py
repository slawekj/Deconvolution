import customtkinter as ctk
import pathlib
from deconvolution import Deconvolver
from threading import Thread
from tkinter import filedialog as fd
from jproperties import Properties
from datetime import datetime


class Gui(ctk.CTk):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.deconvolver = Deconvolver()
        self.default_properties_file = ".properties"
        self.default_signal_files = ".files"

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.title("Peak Deconvolution")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.signal_selection_frame = ctk.CTkFrame(master=self)
        self.signal_selection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.model_selection_frame = ctk.CTkFrame(master=self)
        self.model_selection_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.progress_frame = ctk.CTkFrame(master=self)
        self.progress_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.model_selection_label = ctk.CTkLabel(master=self.signal_selection_frame, text="Signal file(s):")
        self.model_selection_label.pack(pady=12, padx=10)

        self.signal_files_textbox = ctk.CTkTextbox(master=self.signal_selection_frame, wrap="none",
                                                   font=ctk.CTkFont(family="Courier"))
        self.signal_files_textbox.pack(pady=12, padx=10, expand=True, fill="both")
        self.load_signal_files()

        self.select_signal_files_button = ctk.CTkButton(master=self.signal_selection_frame,
                                                        text="Select file(s)...",
                                                        command=lambda: Thread(target=self.select_signal_files).start())
        self.select_signal_files_button.pack(pady=12, padx=10)

        self.clear_selection_button = ctk.CTkButton(master=self.signal_selection_frame,
                                                    text="Clear selection",
                                                    command=lambda: Thread(target=self.clear_files).start())
        self.clear_selection_button.pack(pady=12, padx=10)

        self.model_selection_label = ctk.CTkLabel(master=self.model_selection_frame,
                                                  text="Fitting model properties:")
        self.model_selection_label.pack(pady=12, padx=10)

        self.model_selection_textbox = ctk.CTkTextbox(master=self.model_selection_frame, wrap="none",
                                                      font=ctk.CTkFont(family="Courier"))
        self.model_selection_textbox.pack(pady=12, padx=10, expand=True, fill="both")
        self.load_properties(self.default_properties_file)

        self.model_open_button = ctk.CTkButton(master=self.model_selection_frame,
                                               text="Open...",
                                               command=lambda: Thread(target=self.select_properties_file).start())
        self.model_open_button.pack(pady=12, padx=10)

        self.model_save_button = ctk.CTkButton(master=self.model_selection_frame,
                                               text="Save...",
                                               command=lambda: Thread(target=self.save_properties).start())
        self.model_save_button.pack(pady=12, padx=10)

        self.progress_label = ctk.CTkLabel(master=self.progress_frame, text="Progress:")
        self.progress_label.pack(pady=12, padx=10)

        self.progress_bar = ctk.CTkProgressBar(master=self.progress_frame, orientation="horizontal",
                                               mode="indeterminate")
        self.progress_bar.pack(pady=12, padx=10)
        self.progress_bar.set(0.0)

        self.progress_textbox = ctk.CTkTextbox(master=self.progress_frame, wrap="none",
                                               font=ctk.CTkFont(family="Courier"))
        self.progress_textbox.pack(pady=12, padx=10, expand=True, fill="both")

        self.start_button = ctk.CTkButton(master=self.progress_frame, text="Start",
                                          command=lambda: Thread(target=self.start).start())
        self.start_button.pack(pady=12, padx=10)

        self.stop_button = ctk.CTkButton(master=self.progress_frame, text="Stop",
                                         command=lambda: Thread(target=self.stop_or_reset).start())
        self.stop_button.pack(pady=12, padx=10)

        self.running_experiment = None
        self.reset_experiment()

    def load_properties(self, file_path):
        with open(file_path, "r") as file:
            self.model_selection_textbox.delete(1.0, ctk.END)
            for line in file.readlines():
                self.model_selection_textbox.insert(ctk.END, line)

    def save_default_properties(self):
        with open(self.default_properties_file, "w") as file:
            file.write(self.model_selection_textbox.get("1.0", ctk.END).strip())

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
                file.write(self.model_selection_textbox.get("1.0", ctk.END).strip())

    def load_signal_files(self):
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
            initialdir=pathlib.Path.home(),
            filetypes=filetypes)
        if len(filenames) > 0:
            self.signal_files_textbox.delete("1.0", ctk.END)
        for filename in filenames:
            self.signal_files_textbox.insert(ctk.END, filename + "\n")

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

    def extract_file_names(self):
        filenames = []
        for line in self.signal_files_textbox.get("1.0", ctk.END).split("\n"):
            stripped_line = line.strip()
            if len(stripped_line) > 0:
                filenames.append(stripped_line)
        return filenames

    def extract_properties(self):
        properties = Properties()
        properties.load(self.model_selection_textbox.get("1.0", ctk.END))
        return properties.properties

    def on_closing(self):
        self.save_default_properties()
        self.save_signal_files()
        self.destroy()

    def reset_experiment(self):
        self.progress_label.configure(text="Progress: 0.00%")
        self.progress_textbox.delete(1.0, ctk.END)
        self.progress_bar.stop()
        self.progress_bar.set(0.0)
        self.running_experiment = None
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def start_experiment(self, experiment_label):
        self.progress_label.configure(text="Progress: 0.00%")
        self.progress_textbox.delete(1.0, ctk.END)
        self.progress_bar.start()
        self.running_experiment = experiment_label
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.stop_button.configure(text="Stop")

    def stop_experiment(self):
        self.progress_bar.stop()
        self.running_experiment = None
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.stop_button.configure(text="Reset")

    def is_experiment_in_progress(self):
        return self.running_experiment is not None

    def is_experiment_current(self, experiment_label):
        return self.running_experiment == experiment_label

    def log_progress_line(self, progress_line):
        self.progress_textbox.insert(ctk.END, "[{ts}] {progress_line}\n".format(
            ts=datetime.now().strftime("%H:%M:%S"),
            progress_line=progress_line))

    def log_ok_progress_line(self, progress_line):
        self.progress_textbox.insert(ctk.END, "[{ts}] OK ".format(
            ts=datetime.now().strftime("%H:%M:%S")
        ))
        current_text_length = len(self.progress_textbox.get("1.0", ctk.END))
        self.progress_textbox.tag_add("green_letters",
                                      f"1.0 + {current_text_length - 4} chars",
                                      f"1.0 + {current_text_length - 2} chars")
        self.progress_textbox.tag_config("green_letters", foreground="green")
        self.progress_textbox.insert(ctk.END, "{progress_line}\n".format(
            progress_line=progress_line
        ))

    def log_error_progress_line(self, progress_line):
        self.progress_textbox.insert(ctk.END, "[{ts}] ERROR ".format(
            ts=datetime.now().strftime("%H:%M:%S")
        ))
        current_text_length = len(self.progress_textbox.get("1.0", ctk.END))
        self.progress_textbox.tag_add("red_letters",
                                      f"1.0 + {current_text_length - 7} chars",
                                      f"1.0 + {current_text_length - 2} chars")
        self.progress_textbox.tag_config("red_letters", foreground="red")
        self.progress_textbox.insert(ctk.END, "{progress_line}\n".format(
            progress_line=progress_line
        ))

    def start(self):
        filenames = self.extract_file_names()
        if len(filenames) > 0:
            experiment_label = datetime.now().strftime("experiment_%m_%d_%Y__%H_%M_%S")
            self.start_experiment(experiment_label)
            self.log_progress_line("{exp} started".format(exp=experiment_label))
            properties = self.extract_properties()
            for i in range(len(filenames)):
                if self.is_experiment_current(experiment_label):
                    filename = filenames[i]
                    deconvolution_status = self.deconvolver.deconvolve_single_file(
                        signal_file_abs_path=filename,
                        experiment_label=experiment_label,
                        properties=properties)
                    if self.is_experiment_current(experiment_label):
                        if deconvolution_status.get("exit_code") == 0:
                            self.log_ok_progress_line("{filename}".format(
                                filename=filename
                            ))
                        else:
                            self.log_error_progress_line("{filename}".format(
                                filename=filename
                            ))
                            self.log_progress_line(deconvolution_status.get("error_message").strip())
                        self.progress_label.configure(text=f"Progress: {round((i + 1) / len(filenames) * 100, 2)}%")
            if self.is_experiment_current(experiment_label):
                self.log_progress_line("{exp} finished".format(exp=experiment_label))
                self.stop_experiment()
        else:
            self.log_progress_line("No signal file(s) selected!")
            self.stop_experiment()

    def stop_or_reset(self):
        if self.running_experiment is None:
            self.reset_experiment()
        else:
            previous_experiment = self.running_experiment
            self.stop_experiment()
            self.log_progress_line("{exp} stopped".format(exp=previous_experiment))
