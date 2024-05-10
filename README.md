# Deconvolution
This is a program deconvolving peaks from a signal, typically required in spectroscopy. 
It has a simple user interface to load signal files, control deconvolution parameters, and track progress:

![Screenshot1](resources/Screenshot1.png "Screenshot1")

It uses [Non-Linear Least-Squares Minimization and Curve-Fitting](https://lmfit.github.io//lmfit-py/),
and produces results as text files and pdf figures, e.g.:

![Screenshot2](resources/Screenshot2.png "Screenshot2")

## Requirements

This program is written in Python and requires it to run! It was developed and tested using `Python 3.11.4`.

All additional requirements are listed in `requirements.txt` file:

```commandline
 % cat requirements.txt 
customtkinter
lmfit
matplotlib
pandas
jproperties
```

Additional system libraries may be required, see you operating system's manual if necessary.

## Development

The easiest way to run and develop this project is by calling:
```commandline
% pip install -r requirements.txt
% python src/main.py
```

Happy Deconvolving!
