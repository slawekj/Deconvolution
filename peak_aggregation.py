import pandas as pd
import os
import os.path as path_utils


class PeakAggregator:
    def __init__(self):
        self.peak_keys = ["#", "PeakType", "Center", "Height", "Area", "FWHM", "parameters...", "File"]
        self.all_peaks = {}
        for k in self.peak_keys:
            self.all_peaks[k] = []

    def add_peak(self, index, peak_type, center, height, area, fwhm, parameters, file):
        current_index = len(self.all_peaks["#"])
        self.all_peaks["#"].insert(current_index, index)
        self.all_peaks["PeakType"].insert(current_index, peak_type)
        self.all_peaks["Center"].insert(current_index, center)
        self.all_peaks["Height"].insert(current_index, height)
        self.all_peaks["Area"].insert(current_index, area)
        self.all_peaks["FWHM"].insert(current_index, fwhm)
        self.all_peaks["parameters..."].insert(current_index, parameters)
        self.all_peaks["File"].insert(current_index, file)

    def save_peaks_to_file(self, experiment_label):
        if len(self.all_peaks["File"]) > 0:
            signal_file_abs_path = self.all_peaks["File"][0]
            file_directory = path_utils.dirname(signal_file_abs_path)
            output_dir = path_utils.join(file_directory, experiment_label)
            if not path_utils.exists(output_dir):
                os.mkdir(output_dir)
            all_peaks_df = pd.DataFrame(self.all_peaks)
            all_peaks_df.to_csv(path_or_buf=path_utils.join(output_dir, "all.peaks"),
                                sep="\t", index=False)
