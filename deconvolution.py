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

    def deconvolve_single_file(self, signal_file_abs_path, experiment_label, properties, all_peaks):
        try:
            input_format_separator = optional_property_str(properties.get("input_format_separator"), "\t")
            input_format_header = optional_property_bool(properties.get("input_format_header"), False)
            method = optional_property_str(properties.get("method"), "differential_evolution")
            n_gauss = optional_property_int(properties.get("n_gauss"), 0)
            n_lorentz = optional_property_int(properties.get("n_lorentz"), 0)
            include_background = optional_property_bool(properties.get("include_background"), False)
            gauss_peak_amp_min_default = optional_property_float(
                properties.get("gauss_peak_amp_min_default"), 0.0)
            gauss_peak_amp_max_default = optional_property_float(
                properties.get("gauss_peak_amp_max_default"), 100.0)
            lorentz_peak_amp_min_default = optional_property_float(
                properties.get("lorentz_peak_amp_min_default"),
                0.0)
            lorentz_peak_amp_max_default = optional_property_float(
                properties.get("lorentz_peak_amp_max_default"),
                100.0)
            gauss_peak_sigma_max_default = optional_property_float(
                properties.get("gauss_peak_sigma_max_default"), 100.0)
            lorentz_peak_sigma_max_default = optional_property_float(
                properties.get("lorentz_peak_sigma_max_default"),
                100.0)

            file_directory = path_utils.dirname(signal_file_abs_path)
            file_name_with_extension = path_utils.basename(signal_file_abs_path)
            file_name_root, file_name_extension = path_utils.splitext(file_name_with_extension)

            data = pandas.read_csv(filepath_or_buffer=signal_file_abs_path,
                                   header={True: 0, False: None}[input_format_header],
                                   names=["#Wave", "#Intensity"],
                                   sep=input_format_separator)

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
                    amplitude=dict(
                        min=optional_property_float(properties.get(f"gauss_peak{i + 1}_amp_min"),
                                                    gauss_peak_amp_min_default),
                        max=optional_property_float(properties.get(f"gauss_peak{i + 1}_amp_max"),
                                                    gauss_peak_amp_max_default),
                        value=0.0),
                    center=dict(
                        min=optional_property_float(properties.get(f"gauss_peak{i + 1}_mu_min"), signal_min_x),
                        max=optional_property_float(properties.get(f"gauss_peak{i + 1}_mu_max"), signal_max_x),
                        value=signal_min_x),
                    sigma=dict(
                        min=optional_property_float(properties.get(f"gauss_peak{i + 1}_sigma_min"), 0.0),
                        max=optional_property_float(properties.get(f"gauss_peak{i + 1}_sigma_max"),
                                                    gauss_peak_sigma_max_default),
                        value=0.0))
                composite_params.update(new_params)
                composite_model = composite_model + new_model

            for i in range(n_lorentz):
                new_model = LorentzianModel(prefix=f"lorentz_peak{i + 1}_")
                new_params = new_model.make_params(
                    amplitude=dict(
                        min=optional_property_float(properties.get(f"lorentz_peak{i + 1}_amp_min"),
                                                    lorentz_peak_amp_min_default),
                        max=optional_property_float(properties.get(f"lorentz_peak{i + 1}_amp_max"),
                                                    lorentz_peak_amp_max_default),
                        value=0.0),
                    center=dict(
                        min=optional_property_float(properties.get(f"lorentz_peak{i + 1}_mu_min"), signal_min_x),
                        max=optional_property_float(properties.get(f"lorentz_peak{i + 1}_mu_max"), signal_max_x),
                        value=signal_min_x),
                    sigma=dict(
                        min=optional_property_float(properties.get(f"lorentz_peak{i + 1}_sigma_min"), 0.0),
                        max=optional_property_float(properties.get(f"lorentz_peak{i + 1}_sigma_max"),
                                                    lorentz_peak_sigma_max_default),
                        value=0.0))
                composite_params.update(new_params)
                composite_model = composite_model + new_model

            result = composite_model.fit(
                data=signal,
                x=x,
                params=composite_params,
                method=method)

            output_dir = path_utils.join(file_directory, experiment_label)
            if not path_utils.exists(output_dir):
                os.mkdir(output_dir)

            peak_index = 0
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

            matplotlib.use('SVG')
            plt.clf()
            ax = plt.subplot(111)
            ax.plot(x, signal, label='signal')
            ax.plot(x, result.best_fit, '--', label='fit')

            fit_df = pd.DataFrame(list(zip(x, result.best_fit)), columns=["#Wave", "#Intensity"])
            fit_df.to_csv(
                path_or_buf=path_utils.join(output_dir, file_name_root + ".fit{ex}".format(ex=file_name_extension)),
                sep=input_format_separator,
                index=False,
                header=input_format_header)

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
                               sep=input_format_separator,
                               index=False,
                               header=input_format_header)
                peaks["#"].insert(peak_index, f"%_{peak_index + 1}")
                peaks["PeakType"].insert(peak_index, "Gaussian")
                peaks["Center"].insert(peak_index, center)
                peaks["Height"].insert(peak_index, height)
                peaks["Area"].insert(peak_index, height * sigma / 0.3989)
                peaks["FWHM"].insert(peak_index, fwhm)
                peaks["parameters..."].insert(peak_index, f"{height} {center} ?")
                peaks["File"].insert(peak_index, file_name_root)
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
                               sep=input_format_separator,
                               index=False,
                               header=input_format_header)
                peaks["#"].insert(peak_index, f"%_{peak_index + 1}")
                peaks["PeakType"].insert(peak_index, "Lorentzian")
                peaks["Center"].insert(peak_index, center)
                peaks["Height"].insert(peak_index, height)
                peaks["Area"].insert(peak_index, np.pi)
                peaks["FWHM"].insert(peak_index, fwhm)
                peaks["parameters..."].insert(peak_index, f"{height} {center} ?")
                peaks["File"].insert(peak_index, file_name_root)
                peak_index = peak_index + 1

            all_peaks["#"].extend(peaks["#"])
            all_peaks["PeakType"].extend(peaks["PeakType"])
            all_peaks["Center"].extend(peaks["Center"])
            all_peaks["Height"].extend(peaks["Height"])
            all_peaks["Area"].extend(peaks["Area"])
            all_peaks["FWHM"].extend(peaks["FWHM"])
            all_peaks["parameters..."].extend(peaks["parameters..."])
            all_peaks["File"].extend(peaks["File"])

            if include_background:
                bkg_c = result.best_values["bkg_c"]
                y = [bkg_c for i in x]
                ax.plot(x, y, '--', label=f"Background: {round(bkg_c, 2)}")
                peak_df = pd.DataFrame(list(zip(x, y)), columns=["#Wave", "#Intensity"])
                peak_df.to_csv(path_or_buf=path_utils.join(output_dir,
                                                           file_name_root + ".background{ex}".format(
                                                               ex=file_name_extension)),
                               sep=input_format_separator,
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
            peaks_df = pd.DataFrame(peaks)
            peaks_df.to_csv(path_or_buf=path_utils.join(output_dir, file_name_root + ".final.peaks"),
                            sep="\t", index=False)
            with open(path_utils.join(output_dir, file_name_root + ".model.txt"), "w") as output:
                output.writelines(result.fit_report())
            with open(path_utils.join(output_dir, file_name_root + ".properties"), "w") as output:
                for property in properties:
                    output.write(property + "=" + properties[property] + "\n")
            return 0
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
            return 1


def optional_property_str(prop, default):
    if prop is None:
        return default
    else:
        return prop


def optional_property_bool(prop, default):
    if prop is None:
        return default
    else:
        return prop == "True"


def optional_property_int(prop, default):
    if prop is None:
        return default
    else:
        return int(prop)


def optional_property_float(prop, default):
    if prop is None:
        return default
    else:
        return float(prop)
