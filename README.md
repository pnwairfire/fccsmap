# fccsmap

This package supports the look-up of FCCS fuelbed information by lat/lng or
vector geo spatial data.

## Development

### Install Dependencies@

fccsmap depends on gdal, proj, and netcdf, which must be installed manually.
On a mac, you can do so with [Homebrew](http://brew.sh/):

    brew install homebrew/science/netcdf
    brew install proj
    brew install gdal --with-netcdf --enable-unsupported

On ubuntu, the following should be sufficient:

    sudo apt-get install libnetcdf-dev
    sudo apt-get install proj
    sudo apt-get install libgdal1-1.7.0

Note that the '--with-netcdf' option is required to build gdal with the
netCDF driver. See http://trac.osgeo.org/gdal/wiki/NetCDF for more information.


Run the following to install python dependencies:

    pip install -r requirements.txt

Run the following for installing development dependencies (like running tests):

    pip install -r requirements-test.txt

### Setup Environment

To import fccsmap in development, you'll have to add the repo root directory
to the search path.

## Running tests

Use pytest:

    py.test
    py.test test/fccsmap/

You can also use the ```--collect-only``` option to see a list of all tests.

    py.test --collect-only

See [pytest](http://pytest.org/latest/getting-started.html#getstarted) for more information about

## Installing

### Installing With pip

First, install pip:

    sudo apt-get install python-pip

Then, to install, for example, v0.3.7, use the following:

    sudo pip install git+https://github.com/pnwairfire/fccsmap@v0.1.0

If you get an error like    ```AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex```, it means you need in upgrade pip.  One way to do so is with the following:

    pip install --upgrade pip

## Usage:

### Using the Python Package

TODO: fill this in

### Using the Executables

TODO: fill this in
