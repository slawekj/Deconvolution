from jproperties import Properties
from deconvolution import Deconvolver
import unittest
import sys
import os
sys.path.append(os.path.join(sys.path[0], "..", "src"))


class DeconvolverTest(unittest.TestCase):

    def setUp(self):
        self.d = Deconvolver()

    def test_c_tor(self):
        self.assertIsNotNone(self.d)

    def test_determine_default_limits(self):
        p = Properties()
        limits = self.d.determine_limits(properties=p,
                                         parameter_name="dummy_parameter",
                                         parameter_default_min=0.0,
                                         parameter_default_max=1.0)
        self.assertIsNotNone(limits)
        self.assertEqual(0.0, limits["min"])
        self.assertEqual(1.0, limits["max"])
        self.assertEqual(0.0, limits["value"])

    def test_init_peaks(self):
        peaks = self.d.init_peaks()
        self.assertTrue(isinstance(peaks, type({})))
        for key in peaks.keys():
            self.assertEqual(0, len(peaks[key]))

    def test_add_peak(self):
        peaks = self.d.init_peaks()
        self.d.add_peak(peaks=peaks,
                        index=0,
                        peak_type="dummy type",
                        center=0.0,
                        height=0.0,
                        area=0.0,
                        fwhm=0.0,
                        parameters=[],
                        file="dummy file")
        for key in peaks.keys():
            self.assertEqual(1, len(peaks[key]))

    def test_optional_property_str(self):
        self.assertEqual(
            "default", self.d.optional_property_str(None, "default"))
        self.assertEqual(
            "value", self.d.optional_property_str("value", "default"))

    def test_optional_property_bool(self):
        self.assertEqual(False, self.d.optional_property_bool(None, False))
        self.assertEqual(True, self.d.optional_property_bool("True", False))
        self.assertEqual(False, self.d.optional_property_bool("False", True))

    def test_optional_property_int(self):
        self.assertEqual(4, self.d.optional_property_int(None, 4))
        self.assertEqual(5, self.d.optional_property_int("5", 4))

    def test_optional_property_float(self):
        self.assertEqual(4.5, self.d.optional_property_float(None, 4.5))
        self.assertEqual(5.5, self.d.optional_property_float("5.5", 4.5))


if __name__ == '__main__':
    unittest.main()
