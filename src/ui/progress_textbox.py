import pathlib
import webbrowser
from datetime import datetime

import customtkinter as ctk


def open_experiment_directory(_, directory):
    webbrowser.open(pathlib.Path(directory).as_uri())


class ProgressTextbox(ctk.CTkTextbox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def log_info_progress_line(self, progress_line):
        self.insert(ctk.END, "[{ts}] INFO ".format(
            ts=datetime.now().strftime("%H:%M:%S")
        ))
        current_text_length = len(self.get("1.0", ctk.END))
        self.tag_add("blue_letters",
                     f"1.0 + {current_text_length - 6} chars",
                     f"1.0 + {current_text_length - 2} chars")
        self.tag_config("blue_letters", foreground="blue")
        self.insert(ctk.END, "{progress_line}\n".format(
            progress_line=progress_line
        ))

    def log_ok_progress_line(self, progress_line):
        self.insert(ctk.END, "[{ts}] OK ".format(
            ts=datetime.now().strftime("%H:%M:%S")
        ))
        current_text_length = len(self.get("1.0", ctk.END))
        self.tag_add("green_letters",
                     f"1.0 + {current_text_length - 4} chars",
                     f"1.0 + {current_text_length - 2} chars")
        self.tag_config("green_letters", foreground="green")
        self.insert(ctk.END, "{progress_line}\n".format(
            progress_line=progress_line
        ))

    def log_error_progress_line(self, progress_line):
        self.insert(ctk.END, "[{ts}] ERROR ".format(
            ts=datetime.now().strftime("%H:%M:%S")
        ))
        current_text_length = len(self.get("1.0", ctk.END))
        self.tag_add("red_letters",
                     f"1.0 + {current_text_length - 7} chars",
                     f"1.0 + {current_text_length - 2} chars")
        self.tag_config("red_letters", foreground="red")
        self.insert(ctk.END, "{progress_line}\n".format(
            progress_line=progress_line
        ))

    def log_experiment_hyperlink_line(self, output_directory):
        self.insert(ctk.END, "[{ts}] OPEN ".format(
            ts=datetime.now().strftime("%H:%M:%S")
        ))
        current_text_length = len(self.get("1.0", ctk.END))
        self.tag_add("brown_letters",
                     f"1.0 + {current_text_length - 6} chars",
                     f"1.0 + {current_text_length - 2} chars")
        self.tag_config("brown_letters", foreground="brown")
        self.insert(ctk.END, "{label}\n".format(label=output_directory))
        current_text_length = len(self.get("1.0", ctk.END))
        self.tag_add("hyperlink",
                     f"1.0 + {current_text_length - len(output_directory) - 2} chars",
                     f"1.0 + {current_text_length - 2} chars")
        self.tag_config("hyperlink", foreground="brown", underline=1)
        self.tag_bind("hyperlink", "<Button-1>",
                      lambda event: open_experiment_directory(event, output_directory))
        self.tag_bind("hyperlink", "<Enter>",
                      lambda event: self.configure(cursor="hand2"))
        self.tag_bind("hyperlink", "<Leave>",
                      lambda event: self.configure(cursor=""))
