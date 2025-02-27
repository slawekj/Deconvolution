import pathlib
from threading import Thread
from tkinter import filedialog as fd

import customtkinter as ctk
from jproperties import Properties


class PropertiesFrame(ctk.CTkFrame):
    def __init__(self, default_properties_file, label, **kwargs):
        super().__init__(**kwargs)

        self.default_properties_file = default_properties_file
        self.label = label

        self.model_selection_label = ctk.CTkLabel(master=self, text=label)
        self.model_selection_label.pack(pady=12, padx=10)

        self.model_selection_textbox = ctk.CTkTextbox(master=self, wrap="none", font=ctk.CTkFont(family="Courier"))
        self.model_selection_textbox.pack(pady=12, padx=10, expand=True, fill="both")

        self.load_properties(self.default_properties_file)

        self.model_open_button = ctk.CTkButton(master=self, text="Open...",
                                               command=lambda: Thread(target=self.select_properties_file).start())
        self.model_open_button.pack(pady=12, padx=10)

        self.model_save_button = ctk.CTkButton(master=self, text="Save...",
                                               command=lambda: Thread(target=self.save_properties).start())
        self.model_save_button.pack(pady=12, padx=10)

    def load_properties(self, file_path):
        with open(file_path, "r") as file:
            self.model_selection_textbox.delete(1.0, ctk.END)
            for line in file.readlines():
                self.model_selection_textbox.insert(ctk.END, line)

    def save_default_properties(self):
        with open(self.default_properties_file, "w") as file:
            file.write(self.model_selection_textbox.get(
                "1.0", ctk.END).strip())

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

    def extract_properties(self):
        properties = Properties()
        properties.load(self.model_selection_textbox.get("1.0", ctk.END))
        return properties.properties

    def on_closing(self):
        self.save_default_properties()
