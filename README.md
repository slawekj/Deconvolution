# Deconvolution
This is a program deconvolving peaks from a signal, typically required in spectroscopy, but also useful
for general curve fitting. It has a simple user interface to load signal files, control deconvolution 
parameters, and track progress:

![Screenshot1](resources/Screenshot1.png "Screenshot1")

It uses [Non-Linear Least-Squares Minimization and Curve-Fitting](https://lmfit.github.io//lmfit-py/),
and produces results as text files and pdf figures, e.g.:

![Screenshot2](resources/Screenshot2.png "Screenshot2")

In the example above, `signal` was given as input, and the program was set up to deconvolve
the last visible peak into 6 distinct Gaussians. The plot includes `fit`, which is a sum of detected 
components, i.e. $G_1 + G_2 + ... + G_6$.

## Requirements

This program is written in Python and requires it to run! It was developed and tested using `Python 3.11.4`.

Required Python dependencies are listed in `requirements.txt` file. 
Additional system libraries may be required, see you operating system's manual if necessary.

## Development

The easiest way to run and develop this project is by installing dependencies first:
```commandline
pip install -r requirements.txt
```

, and then running the main program:
```commandline
python src/main.py
```

Happy Deconvolving!
