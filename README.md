# fccsmap

This package supports the look-up of FCCS fuelbed information by lat/lng or
vector geo spatial data.

***This software is provided for research purposes only. It's output may
not accurately reflect observed data due to numerous reasons. Data are
provisional; use at own risk.***

## Python 2 and 3 Support

This package was originally developed to support python 2.7, but has since
been refactored to support 3.5. Attempts to support both 2.7 and 3.5 have
been made but are not guaranteed.

## External Dependencies

Whether cloning the repo or installing with pip, you'll first need to
manually install numpy, gdal, proj, and netcdf, which fccsmap depends on.  These
instructions assume you already have python and pip installed, as well as
C and C++ compilers, etc.

### Mac

On a mac, using [Homebrew](http://brew.sh/):

    brew install homebrew/science/netcdf
    brew install proj
    brew install gdal --with-netcdf --enable-unsupported

Note that the '--with-netcdf' option is required to build gdal with the
netCDF driver. See http://trac.osgeo.org/gdal/wiki/NetCDF for more information.

Additionally, you'll need numpy and gdal python bindings.  These used to be
baked into setup.py, but the version available for install depends
on your platform.

    pip install numpy
    gdal-config --version
    pip install gdal==`gdal-config --version`

Note that another source for Open Source GIS packages is
http://www.kyngchaos.com/software/unixport.

### Ubuntu, 12.04 LTS (precise)

    sudo apt-get update
    sudo apt-get install -y python3 python3-dev python3-pip
    sudo pip3 install --upgrade pip3
    sudo apt-get install -y libnetcdf-dev proj
    sudo apt-get install -y libgdal-dev
    sudo apt-get install -y python3-numpy python3-gdal
    sudo apt-get install -y libxml2-dev libxslt1-dev

### Ubuntu, 16.04 LTS (Xenial)

    sudo apt-get update
    sudo apt-get install -y python3 python3-dev python3-pip
    sudo pip3 install distribute
    sudo apt-get install -y libnetcdf-dev libproj-dev
    sudo apt-get install -y libgdal-dev
    sudo apt-get install -y python3-numpy python3-gdal
    sudo apt-get install -y libxml2-dev libxslt1-dev

## Development

### Clone Repo

Via ssh:

    git clone git@github.com:pnwairfire/fccsmap.git

or http:

    git clone https://github.com/pnwairfire/fccsmap.git

### Install Python Dependencies

#### Main dependencies

After installing the non-python dependencies (mentioned above), run the
following to install required python packages:

    pip install --trusted-host pypi.smoke.airfire.org -r requirements.txt

#### Dev and test dependencies

Run the following to install packages required for development and testing:

    pip install -r requirements-test.txt
    pip install -r requirements-dev.txt

#### Notes

##### pip issues

If you get an error like    ```AttributeError: 'NoneType' object has no
attribute 'skip_requirements_regex```, it means you need in upgrade
pip. One way to do so is with the following:

    pip install --upgrade pip

##### python gdal issues

If, when you use fccsmap, you get the following error:

    *** Error: No module named _gdal_array

it's because your osgeo package (/path/to/site-packages/osgeo/) is
missing _gdal_array.so.  This happens when gdal is built on a
machine that lacks numpy.  The ```--no-binary :all:``` in the pip
install command, above, is meant to fix this issue.  If it doesn't work,
try uninstalling the gdal package and then re-installing it individually
with the ```--no-binary``` option to pip:

    pip uninstall -y GDAL
    pip install --no-binary :all: gdal==<VERSION>

If this doesn't work, uninstall gdal, and then install it manually:

    pip uninstall -y GDAL
    wget https://pypi.python.org/packages/source/G/GDAL/GDAL-<VERSION>.tar.gz
    tar xzf GDAL-<VERSION>.tar.gz
    cd GDAL-<VERSION>
    python setup.py install

Links:

 - http://trac.osgeo.org/gdal/wiki/DownloadSource
 - http://gis.stackexchange.com/questions/28966/python-gdal-package-missing-header-file-when-installing-via-pip
 - [pygdal](https://github.com/dezhin/pygdal)

### Setup Environment

To import fccsmap in development, you'll have to add the repo root directory
to the search path.

## Running tests

Use pytest:

    py.test
    py.test test/unit/fccsmap/test_lookup.py

You can also use the ```--collect-only``` option to see a list of all tests.

    py.test --collect-only

See [pytest](http://pytest.org/latest/getting-started.html#getstarted) for more information about

## Installing

First install the non-python dependencies (mentioned above).

### Installing With pip

First, install pip (with sudo if necessary):

    apt-get install python-pip

Then, to install, for example, version v2.0.0, use the following (with
sudo if necessary):

    pip install --no-binary gdal --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple fccsmap==2.0.0

See the Development > Install Dependencies > Notes section, above, for
notes on resolving pip and gdal issues.

## Usage:

### Using the Python Package

TODO: fill this in

### Using the Executables

#### fccsmap

```fccsmap``` returns fuelbed information by geographical location or region.
To see it's options and examples, use the '-h' option:

    $ fccsmap -h
