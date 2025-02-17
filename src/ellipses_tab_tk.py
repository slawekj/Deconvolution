import customtkinter as ctk


class EllipsesTab:
    def __init__(self, tab: ctk.CTkFrame):
        self.tab = tab

        self.textbox = ctk.CTkTextbox(master=self.tab, wrap="none",
                                      font=ctk.CTkFont(family="Courier"))

        self.textbox.insert(ctk.END,"""
Currently, the ellipses tool offers a command line interface (CLI) only, usage:
        
    python src/ellipses.py \\
        --long-diameter-file sample_data/ellipses/coated_63_long.tsv \\
        --short-diameter-file sample_data/ellipses/coated_63_short.tsv \\
        --output-file coated_63_extrapolation.dpt

    sample_data/ellipses/coated_63_long.tsv sample_data/ellipses/coated_63_short.tsv

    Ellipse r1=65.00 r2=54.17: avg z: 16.52
    Ring r1=130.00 r2=108.33: avg z: 15.51
    Ring r1=195.00 r2=162.50: avg z: 12.81
    Ring r1=260.00 r2=216.67: avg z: 10.04
    Ring r1=325.00 r2=270.83: avg z: 8.57
    Ring r1=390.00 r2=325.00: avg z: 8.38
    Ring r1=455.00 r2=379.17: avg z: 8.22
    Ring r1=520.00 r2=433.33: avg z: 7.37
    Ring r1=585.00 r2=487.50: avg z: 6.59
    Ring r1=650.00 r2=541.67: avg z: 5.47
    Ring r1=715.00 r2=595.83: avg z: 5.08
    Ring r1=780.00 r2=650.00: avg z: 5.08
    Ring r1=845.00 r2=704.17: avg z: 4.47
    Ring r1=910.00 r2=758.33: avg z: 3.02
    Ring r1=975.00 r2=812.50: avg z: 2.15

This sample execution will also produce a coated_63_extrapolation.dpt file.
It will also 2D plot the extrapolation.
        """)

        self.textbox.pack(
            pady=12, padx=10, expand=True, fill="both")

    def on_closing(self):
        # Perform any cleanup or saving actions here
        pass
