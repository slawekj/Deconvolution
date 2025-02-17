import customtkinter as ctk

from src.deconvolution_tab_tk import DeconvolutionTab


class GuiTk(ctk.CTk):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set the window size
        window_width = 800
        window_height = 600
        self.geometry(f"{window_width}x{window_height}")

        # Calculate the center position
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)

        # Set the window position to the center of the screen
        self.geometry(f"+{center_x}+{center_y}")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.title("Miscellaneous Tools")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create tab view
        self.tab_view = ctk.CTkTabview(master=self)
        self.tab_view.pack(expand=True, fill="both")

        # Create tabs
        self.deconvolution_tab = DeconvolutionTab(self.tab_view.add("Deconvolution"))
        self.ellipses_tab = self.tab_view.add("Ellipses")

        # Add simple label to Tab 2
        self.label_janusz = ctk.CTkLabel(master=self.ellipses_tab, text="Ellipses tool coming soon...")
        self.label_janusz.pack(pady=12, padx=10)

    def on_closing(self):
        self.deconvolution_tab.on_closing()
        self.destroy()
