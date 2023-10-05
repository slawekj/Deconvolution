import traceback
import sys
import lmfit.lineshapes
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lmfit.models import ConstantModel, GaussianModel, LorentzianModel
import os
import os.path as path_utils
import pandas


class Deconvolver:

    def deconvolve_single_file(self, signal_file_abs_path, experiment_label, properties):
        output_dir = None
        try:
            input_format_separator = self.optional_property_str(properties.get("input_format_separator"), "\t+")
            output_format_separator = self.optional_property_str(properties.get("output_format_separator"), "\t")
            input_format_header = self.optional_property_bool(properties.get("input_format_header"), False)
            output_format_header = self.optional_property_bool(properties.get("output_format_header"), False)
            method = self.optional_property_str(properties.get("method"), "differential_evolution")
            n_gauss = self.optional_property_int(properties.get("n_gauss"), 0)
            n_lorentz = self.optional_property_int(properties.get("n_lorentz"), 0)
            include_background = self.optional_property_bool(properties.get("include_background"), False)
            gauss_peak_amp_min_default = self.optional_property_float(
                properties.get("gauss_peak_amp_min_default"), 0.0)
            gauss_peak_amp_max_default = self.optional_property_float(
                properties.get("gauss_peak_amp_max_default"), 100.0)
            lorentz_peak_amp_min_default = self.optional_property_float(
                properties.get("lorentz_peak_amp_min_default"),
                0.0)
            lorentz_peak_amp_max_default = self.optional_property_float(
                properties.get("lorentz_peak_amp_max_default"),
                100.0)
            gauss_peak_sigma_min_default = self.optional_property_float(
                properties.get("gauss_peak_sigma_min_default"), 0.0)
            gauss_peak_sigma_max_default = self.optional_property_float(
                properties.get("gauss_peak_sigma_max_default"), 100.0)
            lorentz_peak_sigma_min_default = self.optional_property_float(
                properties.get("lorentz_peak_sigma_min_default"),
                0.0)
            lorentz_peak_sigma_max_default = self.optional_property_float(
                properties.get("lorentz_peak_sigma_max_default"),
                100.0)

            file_directory = path_utils.dirname(signal_file_abs_path)
            file_name_with_extension = path_utils.basename(signal_file_abs_path)
            file_name_root, file_name_extension = path_utils.splitext(file_name_with_extension)
            output_dir = path_utils.join(file_directory, experiment_label)
            path_utils.exists(output_dir) or os.mkdir(output_dir)

            data = pandas.read_csv(filepath_or_buffer=signal_file_abs_path,
                                   header={True: 0, False: None}[input_format_header],
                                   names=["#Wave", "#Intensity"],
                                   sep=input_format_separator,
                                   engine="python")

            x = data["#Wave"].tolist()
            signal = data["#Intensity"].tolist()

            signal_min_x = min(x)
            signal_max_x = max(x)
            signal_min_y = min(signal)
            signal_max_y = max(signal)

            constant_model = ConstantModel(prefix="bkg_")
            constant_params = constant_model.make_params(
                c=dict(
                    min=signal_min_y,
                    max=signal_max_y,
                    vary=include_background,
                    value=0.0))
            composite_model = constant_model
            composite_params = constant_params

            for i in range(n_gauss):
                new_model = GaussianModel(prefix=f"gauss_peak{i + 1}_")
                new_params = new_model.make_params(
                    amplitude=self.determine_limits(properties, f"gauss_peak{i + 1}_amp", gauss_peak_amp_min_default,
                                                    gauss_peak_amp_max_default),
                    center=self.determine_limits(properties, f"gauss_peak{i + 1}_mu", signal_min_x, signal_max_x),
                    sigma=self.determine_limits(properties, f"gauss_peak{i + 1}_sigma", gauss_peak_sigma_min_default,
                                                gauss_peak_sigma_max_default))
                composite_params.update(new_params)
                composite_model = composite_model + new_model

            for i in range(n_lorentz):
                new_model = LorentzianModel(prefix=f"lorentz_peak{i + 1}_")
                new_params = new_model.make_params(
                    amplitude=self.determine_limits(properties, f"lorentz_peak{i + 1}_amp",
                                                    lorentz_peak_amp_min_default, lorentz_peak_amp_max_default),
                    center=self.determine_limits(properties, f"lorentz_peak{i + 1}_mu", signal_min_x, signal_max_x),
                    sigma=self.determine_limits(properties, f"lorentz_peak{i + 1}_sigma",
                                                lorentz_peak_sigma_min_default,
                                                lorentz_peak_sigma_max_default))
                composite_params.update(new_params)
                composite_model = composite_model + new_model

            result = composite_model.fit(
                data=signal,
                x=x,
                params=composite_params,
                method=method)

            peak_index = 0
            matplotlib.use("SVG")
            plt.clf()
            ax = plt.subplot(111)
            ax.plot(x, signal, label='signal')
            ax.plot(x, result.best_fit, '--', label='fit')

            fit_df = pd.DataFrame(list(zip(x, result.best_fit)), columns=["#Wave", "#Intensity"])
            fit_df.to_csv(
                path_or_buf=path_utils.join(output_dir,
                                            file_name_root + ".fit{ex}".format(ex=file_name_extension)),
                sep=output_format_separator,
                index=False,
                header=input_format_header)
            peaks = self.init_peaks()
            for i in range(n_gauss):
                amp = result.best_values[f"gauss_peak{i + 1}_amplitude"]
                center = result.best_values[f"gauss_peak{i + 1}_center"]
                sigma = result.best_values[f"gauss_peak{i + 1}_sigma"]
                height = 0.3989423 * amp / max(1e-15, sigma)
                fwhm = 2.3548200 * sigma
                y = [lmfit.lineshapes.gaussian(i, amp, center, sigma) for i in x]
                ax.fill(x, y,
                        label=f"G{i + 1}: \u0391: {round(amp, 2)}, \u03bc: {round(center, 2)}, \u03c3: {round(sigma, 2)}",
                        alpha=0.1)
                peak_df = pd.DataFrame(list(zip(x, y)), columns=["#Wave", "#Intensity"])
                peak_df.to_csv(path_or_buf=path_utils.join(output_dir,
                                                           file_name_root + ".gauss_peak{n}{ex}".format(n=i + 1,
                                                                                                        ex=file_name_extension)),
                               sep=output_format_separator,
                               index=False,
                               header=input_format_header)
                self.add_peak(
                    peaks=peaks,
                    index=f"%_{peak_index + 1}",
                    peak_type="Gaussian",
                    center=center,
                    height=height,
                    area=height * sigma / 0.3989,
                    fwhm=fwhm,
                    parameters=f"{height} {center} ?",
                    file=signal_file_abs_path)
                peak_index = peak_index + 1

            for i in range(n_lorentz):
                amp = result.best_values[f"lorentz_peak{i + 1}_amplitude"]
                center = result.best_values[f"lorentz_peak{i + 1}_center"]
                sigma = result.best_values[f"lorentz_peak{i + 1}_sigma"]
                height = 0.3183099 * amp / max(1e-15, sigma)
                fwhm = 2.0 * sigma
                y = [lmfit.lineshapes.lorentzian(i, amp, center, sigma) for i in x]
                ax.fill(x, y,
                        label=f"L{i + 1}: \u0391: {round(amp, 2)}, \u03bc: {round(center, 2)}, \u03c3: {round(sigma, 2)}",
                        alpha=0.1)
                peak_df = pd.DataFrame(list(zip(x, y)), columns=["#Wave", "#Intensity"])
                peak_df.to_csv(path_or_buf=path_utils.join(output_dir,
                                                           file_name_root + ".lorentz_peak{n}{ex}".format(n=i + 1,
                                                                                                          ex=file_name_extension)),
                               sep=output_format_separator,
                               index=False,
                               header=input_format_header)
                self.add_peak(
                    peaks=peaks,
                    index=f"%_{peak_index + 1}",
                    peak_type="Lorentzian",
                    center=center,
                    height=height,
                    area=np.pi,
                    fwhm=fwhm,
                    parameters=f"{height} {center} ?",
                    file=signal_file_abs_path)
                peak_index = peak_index + 1

            if include_background:
                bkg_c = result.best_values["bkg_c"]
                y = [bkg_c for _ in x]
                ax.plot(x, y, '--', label=f"Background: {round(bkg_c, 2)}")
                peak_df = pd.DataFrame(list(zip(x, y)), columns=["#Wave", "#Intensity"])
                peak_df.to_csv(path_or_buf=path_utils.join(output_dir,
                                                           file_name_root + ".background{ex}".format(
                                                               ex=file_name_extension)),
                               sep=output_format_separator,
                               index=False,
                               header=input_format_header)
            ax.legend(loc="upper center",
                      bbox_to_anchor=(0.5, -0.05),
                      fancybox=True,
                      shadow=True,
                      ncol=3)
            plt.savefig(path_utils.join(output_dir, file_name_root + ".pdf"),
                        format="pdf",
                        bbox_inches="tight")
            with open(path_utils.join(output_dir, file_name_root + ".model.txt"), "w") as output:
                output.writelines(result.fit_report())
            peaks_df = pd.DataFrame(peaks)
            peaks_df.to_csv(path_or_buf=path_utils.join(output_dir, file_name_root + ".peaks"),
                            sep=output_format_separator, index=False)
            aggregate_peaks_file = path_utils.join(output_dir, "all.peaks")
            if path_utils.exists(aggregate_peaks_file):
                existing_peaks_df = pd.read_csv(filepath_or_buffer=aggregate_peaks_file,
                                                sep=output_format_separator)
                if signal_file_abs_path not in existing_peaks_df["File"].values:
                    peaks_df.to_csv(path_or_buf=aggregate_peaks_file, sep=output_format_separator, index=False,
                                    mode="a",
                                    header=False)
            else:
                peaks_df.to_csv(path_or_buf=aggregate_peaks_file, sep=output_format_separator, index=False, header=True)
            output = {
                "exit_code": 0,
                "output_dir": output_dir
            }
            return output
        except Exception as e:
            print(traceback.format_exc(), file=sys.stderr)
            error_log_path = path_utils.join(output_dir, "error.log")
            if output_dir is not None:
                print("ERROR. Error processing {label}, file: {file}, with properties: {properties}".format(
                    label=experiment_label,
                    file=signal_file_abs_path,
                    properties=properties),
                    file=open(path_utils.join(output_dir, "error.log"), "a"))
                print(traceback.format_exc(), file=open(error_log_path, "a"))
            output = {
                "exit_code": 1,
                "output_dir": output_dir,
                "error_message": "{message}, see more details: {error_log}\n".format(message=str(e),
                                                                                     error_log=error_log_path)
            }
            return output
        finally:
            with open(path_utils.join(output_dir, "experiment.properties"), "w") as output:
                for p in properties:
                    output.write(p + "=" + properties[p] + "\n")

    def determine_limits(self, properties, parameter_name, parameter_default_min, parameter_default_max):
        limits = dict()
        if properties.get(parameter_name + "_min"):
            limits["min"] = self.optional_property_float(properties.get(parameter_name + "_min"), parameter_default_min)
        else:
            limits["min"] = parameter_default_min
        if properties.get(parameter_name + "_max"):
            limits["max"] = self.optional_property_float(properties.get(parameter_name + "_max"), parameter_default_max)
        else:
            limits["max"] = parameter_default_max
        if properties.get(parameter_name + "_value"):
            limits["value"] = self.optional_property_float(properties.get(parameter_name + "_value"),
                                                           parameter_default_min)
        else:
            limits["value"] = parameter_default_min
        if properties.get(parameter_name + "_vary"):
            limits["vary"] = self.optional_property_bool(properties.get(parameter_name + "_vary"), True)
        return limits

    @staticmethod
    def init_peaks():
        peaks = {
            "#": [],
            "PeakType": [],
            "Center": [],
            "Height": [],
            "Area": [],
            "FWHM": [],
            "parameters...": [],
            "File": []
        }
        return peaks

    @staticmethod
    def add_peak(peaks, index, peak_type, center, height, area, fwhm, parameters, file):
        current_index = len(peaks["#"])
        peaks["#"].insert(current_index, index)
        peaks["PeakType"].insert(current_index, peak_type)
        peaks["Center"].insert(current_index, center)
        peaks["Height"].insert(current_index, height)
        peaks["Area"].insert(current_index, area)
        peaks["FWHM"].insert(current_index, fwhm)
        peaks["parameters..."].insert(current_index, parameters)
        peaks["File"].insert(current_index, file)

    @staticmethod
    def optional_property_str(prop, default):
        if prop is None:
            return default
        else:
            return prop

    @staticmethod
    def optional_property_bool(prop, default):
        if prop is None:
            return default
        else:
            return prop == "True"

    @staticmethod
    def optional_property_int(prop, default):
        if prop is None:
            return default
        else:
            return int(prop)

    @staticmethod
    def optional_property_float(prop, default):
        if prop is None:
            return default
        else:
            return float(prop)
