# install with pyinstaller --noconfirm --onedir --windowed --add-data "/opt/homebrew/lib/python3.11/site-packages/customtkinter:customtkinter/" /Users/janusz/PycharmProjects/Deconvolution/main.py

import deconvolution as d

import pathlib
import customtkinter as ctk
from threading import Thread
from tkinter import filedialog as fd
from jproperties import Properties
from datetime import datetime

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


def save_properties():
    with open(".properties", "w") as file:
        file.write(model_selection_textbox.get("1.0", ctk.END).strip())


def on_closing():
    save_properties()
    with open(".files", "w") as file:
        file.write(signal_files_textbox.get("1.0", ctk.END).strip())
    app.destroy()


app = ctk.CTk()
app.title("Peak Deconvolution")
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.grid_columnconfigure(2, weight=1)
app.grid_rowconfigure(0, weight=1)
app.protocol("WM_DELETE_WINDOW", on_closing)

signal_selection_frame = ctk.CTkFrame(master=app)
signal_selection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

model_selection_frame = ctk.CTkFrame(master=app)
model_selection_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

progress_frame = ctk.CTkFrame(master=app)
progress_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

model_selection_label = ctk.CTkLabel(master=signal_selection_frame, text="Signal file(s):")
model_selection_label.pack(pady=12, padx=10)


def clear_selection():
    signal_files_textbox.delete(1.0, ctk.END)


def select_files():
    filetypes = (
        ('Text files', '*.txt'),
        ('All files', '*.*')
    )

    filenames = fd.askopenfilenames(
        title='Open file(s)',
        initialdir=pathlib.Path.home(),
        filetypes=filetypes)

    signal_files_textbox.delete("1.0", ctk.END)
    for filename in filenames:
        signal_files_textbox.insert(ctk.END, filename + "\n")


signal_files_textbox = ctk.CTkTextbox(master=signal_selection_frame, wrap="none")
signal_files_textbox.pack(pady=12, padx=10, expand=True, fill="both")
with open(".files", "r") as file:
    for line in file.readlines():
        signal_files_textbox.insert(ctk.END, line)

select_file_button = ctk.CTkButton(master=signal_selection_frame, text="Select file(s)",
                                   command=lambda: Thread(target=select_files).start())
select_file_button.pack(pady=12, padx=10)

clear_selection_button = ctk.CTkButton(master=signal_selection_frame, text="Clear selection",
                                       command=lambda: Thread(target=clear_selection).start())
clear_selection_button.pack(pady=12, padx=10)

model_selection_label = ctk.CTkLabel(master=model_selection_frame, text="Fitting model:")
model_selection_label.pack(pady=12, padx=10)

model_selection_textbox = ctk.CTkTextbox(master=model_selection_frame, wrap="none")
model_selection_textbox.pack(pady=12, padx=10, expand=True, fill="both")
with open(".properties", "r") as file:
    for line in file.readlines():
        model_selection_textbox.insert(ctk.END, line)

model_save_button = ctk.CTkButton(master=model_selection_frame, text="Save",
                                  command=lambda: Thread(target=save_properties).start())
model_save_button.pack(pady=12, padx=10)

progress_label = ctk.CTkLabel(master=progress_frame, text="Progress:")
progress_label.pack(pady=12, padx=10)

progress_bar = ctk.CTkProgressBar(master=progress_frame, orientation="horizontal", mode="indeterminate")
progress_bar.pack(pady=12, padx=10)
progress_bar.set(0.0)

progress_textbox = ctk.CTkTextbox(master=progress_frame, wrap="none")
progress_textbox.pack(pady=12, padx=10, expand=True, fill="both")


def go():
    filenames = []
    for line in signal_files_textbox.get("1.0", ctk.END).split("\n"):
        stripped_line = line.strip()
        if len(stripped_line) > 0:
            filenames.append(stripped_line)
    properties = Properties()
    properties.load(model_selection_textbox.get("1.0", ctk.END))
    experiment_label = datetime.now().strftime("%m_%d_%Y__%H_%M_%S")
    if len(filenames) > 0:
        progress_label.configure(text="Progress: 0.00%")
        progress_bar.start()
        progress_textbox.delete(1.0, ctk.END)
        for i in range(len(filenames)):
            filename = filenames[i]
            deconvolution_status = d.deconvolve(filename, experiment_label, properties.properties)
            progress_textbox.insert(ctk.END,
                                    "OK: " + filename + "\n" if deconvolution_status == 0 else "ERROR: " + filename + "\n")
            progress_label.configure(text=f"Progress: {round((i + 1) / len(filenames) * 100, 2)}%")
        progress_bar.stop()
    else:
        progress_label.configure(text="Progress:")
        progress_bar.set(0.0)
        progress_textbox.delete(1.0, ctk.END)
        progress_textbox.insert(ctk.END, "no signal file(s) selected")


go_button = ctk.CTkButton(master=progress_frame, text="Go!", command=lambda: Thread(target=go).start())
go_button.pack(pady=12, padx=10)

app.mainloop()
