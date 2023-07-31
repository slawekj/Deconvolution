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

        self.signal_files_textbox = ctk.CTkTextbox(master=self.signal_selection_frame, wrap="none")
        self.signal_files_textbox.pack(pady=12, padx=10, expand=True, fill="both")
        with open(".files", "r") as file:
            for line in file.readlines():
                self.signal_files_textbox.insert(ctk.END, line)

        self.select_file_button = ctk.CTkButton(master=self.signal_selection_frame, text="Select file(s)",
                                                command=lambda: Thread(target=self.select_files).start())
        self.select_file_button.pack(pady=12, padx=10)

        self.clear_selection_button = ctk.CTkButton(master=self.signal_selection_frame, text="Clear selection",
                                                    command=lambda: Thread(target=self.clear_selection).start())
        self.clear_selection_button.pack(pady=12, padx=10)

        self.model_selection_label = ctk.CTkLabel(master=self.model_selection_frame, text="Fitting model:")
        self.model_selection_label.pack(pady=12, padx=10)

        self.model_selection_textbox = ctk.CTkTextbox(master=self.model_selection_frame, wrap="none")
        self.model_selection_textbox.pack(pady=12, padx=10, expand=True, fill="both")
        with open(".properties", "r") as file:
            for line in file.readlines():
                self.model_selection_textbox.insert(ctk.END, line)

        self.model_save_button = ctk.CTkButton(master=self.model_selection_frame, text="Save",
                                               command=lambda: Thread(target=self.save_properties).start())
        self.model_save_button.pack(pady=12, padx=10)

        self.progress_label = ctk.CTkLabel(master=self.progress_frame, text="Progress:")
        self.progress_label.pack(pady=12, padx=10)

        self.progress_bar = ctk.CTkProgressBar(master=self.progress_frame, orientation="horizontal",
                                               mode="indeterminate")
        self.progress_bar.pack(pady=12, padx=10)
        self.progress_bar.set(0.0)

        self.progress_textbox = ctk.CTkTextbox(master=self.progress_frame, wrap="none")
        self.progress_textbox.pack(pady=12, padx=10, expand=True, fill="both")

        self.go_button = ctk.CTkButton(master=self.progress_frame, text="Go!",
                                       command=lambda: Thread(target=self.go).start())
        self.go_button.pack(pady=12, padx=10)

        self.deconvolver = Deconvolver()

    def save_properties(self):
        with open(".properties", "w") as file:
            file.write(self.model_selection_textbox.get("1.0", ctk.END).strip())

    def on_closing(self):
        self.save_properties()
        with open(".files", "w") as file:
            file.write(self.signal_files_textbox.get("1.0", ctk.END).strip())
        self.destroy()

    def clear_selection(self):
        self.signal_files_textbox.delete(1.0, ctk.END)

    def go(self):
        filenames = []
        for line in self.signal_files_textbox.get("1.0", ctk.END).split("\n"):
            stripped_line = line.strip()
            if len(stripped_line) > 0:
                filenames.append(stripped_line)
        properties = Properties()
        properties.load(self.model_selection_textbox.get("1.0", ctk.END))
        experiment_label = datetime.now().strftime("experiment_%m_%d_%Y__%H_%M_%S")
        if len(filenames) > 0:
            self.progress_label.configure(text="Progress: 0.00%")
            self.progress_bar.start()
            self.progress_textbox.delete(1.0, ctk.END)
            self.progress_textbox.insert(ctk.END, "{ts}: start\n".format(
                ts=datetime.now().strftime("%H:%M:%S")))
            for i in range(len(filenames)):
                filename = filenames[i]
                deconvolution_status = self.deconvolver.deconvolve(
                    signal_file_abs_path=filename,
                    experiment_label=experiment_label,
                    properties=properties.properties)
                self.progress_textbox.insert(ctk.END, "{ts}: {status} {filename}\n".format(
                    ts=datetime.now().strftime("%H:%M:%S"),
                    status={True: "OK", False: "ERROR"}[deconvolution_status == 0],
                    filename=filename
                ))
                self.progress_label.configure(text=f"Progress: {round((i + 1) / len(filenames) * 100, 2)}%")
            self.progress_bar.stop()
            self.progress_textbox.insert(ctk.END, "{ts}: finished\n".format(
                ts=datetime.now().strftime("%H:%M:%S")
            ))
        else:
            self.progress_label.configure(text="Progress:")
            self.progress_bar.set(0.0)
            self.progress_textbox.delete(1.0, ctk.END)
            self.progress_textbox.insert(ctk.END, "no signal file(s) selected")

    def select_files(self):
        filetypes = (
            ('Text files', '*.txt'),
            ('All files', '*.*')
        )

        filenames = fd.askopenfilenames(
            title='Open file(s)',
            initialdir=pathlib.Path.home(),
            filetypes=filetypes)

        self.signal_files_textbox.delete("1.0", ctk.END)
        for filename in filenames:
            self.signal_files_textbox.insert(ctk.END, filename + "\n")
