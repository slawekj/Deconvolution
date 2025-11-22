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

This program is written in Python and requires it to run! It was developed and tested using `Python 3.11.4`
on Mac OS but it will also run on Windows and Linux. 

### Mac OS Installation guide

First, install [Brew](https://brew.sh/) package manager:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
, then install the required system dependencies:
```
brew install python python-tk poetry
```

## Development

The easiest way to run and develop this project is by installing dependencies with Poetry:
```commandline
poetry install
```

, and then running the GUI:
```commandline
poetry run python gui.py
```

, or a CLI:
```commandline
poetry run python src/logic/ellipses.py
```

Also, you can test the source code by:
```commandline
poetry run python -m unittest discover -v -s src/tests
```

Happy Deconvolving!
