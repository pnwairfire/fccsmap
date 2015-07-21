# fccsmap

This package supports the look-up of FCCS fuelbed information by lat/lng or
vector geo spatial data.

## Non-python Dependencies

Whether cloning the repo or installing with pip, you'll first need to
manually install gdal, proj, and netcdf, which fccsmap depends on.

On a mac, you can do so with [Homebrew](http://brew.sh/):

    brew install homebrew/science/netcdf
    brew install proj
    brew install gdal --with-netcdf --enable-unsupported

Note that the '--with-netcdf' option is required to build gdal with the
netCDF driver. See http://trac.osgeo.org/gdal/wiki/NetCDF for more information.

On ubuntu, the following should be sufficient:

    sudo apt-get install libnetcdf-dev
    sudo apt-get install proj
    sudo apt-get install python-gdal
    sudo apt-get install libgdal1-1.7.0

## Development

### Clone Repo

Via ssh:

    git clone git@github.com:pnwairfire/fccsmap.git

or http:

    git clone https://github.com/pnwairfire/fccsmap.git

### Install Dependencies@

After installing the non-python dependencies (mentioned above), run the
following to install required python packages:

    pip install --no-binary gdal -r requirements.txt

Run the following to install packages required for development and testing:

    pip install -r requirements-test.txt
    pip install -r requirements-dev.txt

#### Notes

##### pip issues

If you get an error like    ```AttributeError: 'NoneType' object has no
attribute 'skip_requirements_regex```, it means you need in upgrade
pip. One way to do so is with the following:

    pip install --upgrade pip

##### gdal issues

If, when you use fccsmap, you get the following error:

    *** Error: No module named _gdal_array

it's because your osgeo package (/path/to/site-packages/osgeo/) is
missing _gdal_array.so.  This happens when gdal is built on a
machine that lacks numpy.  The ```--no-binary :all:``` in the pip
install command, above, is meant to fix this issue.  If it doesn't work,
try uninstalling the gdal package and then re-installing it individually
with the ```--no-binary``` option to pip:

    pip uninstall -y GDAL
    pip install --no-binary :all: gdal==1.11.2

If this doesn't work, uninstall gdal, and then install it manually:

    pip uninstall -y GDAL
    wget https://pypi.python.org/packages/source/G/GDAL/GDAL-1.11.2.tar.gz
    tar xzf GDAL-1.11.2.tar.gz
    cd GDAL-1.11.2
    python setup.py install

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

First install the non-python dependencies (mentioned above).

### Installing With pip

First, install pip (with sudo if necessary):

    apt-get install python-pip

Then, to install, for example, version 0.1.7, use the following (with
sudo if necessary):

    pip install --no-binary gdal --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple fccsmap==0.1.7

See the Development > Install Dependencies > Notes section, above, for
notes on resolving pip and gdal issues.

## Usage:

### Using the Python Package

TODO: fill this in

### Using the Executables

#### fccsmap

```fccsmap``` returns fuelbed information by geographical location or region.
To see it's options, use the '-h' option:

    $ fccsmap -h

##### Examples

Here's an example that looks up the fuelbeds around Snoqualmie pass

    $ fccsmap --log-level=DEBUG -g '{
          "type": "MultiPolygon",
          "coordinates": [
            [
              [
                [-121.4522115, 47.4316976],
                [-121.3990506, 47.4316976],
                [-121.3990506, 47.4099293],
                [-121.4522115, 47.4099293],
                [-121.4522115, 47.4316976]
              ]
            ]
          ]
        }'

This one looks up fuelbeds in WA state

    $ fccsmap --log-level=DEBUG -g '{
          "type": "MultiPolygon",
          "coordinates": [
              [
                  [
                      [-125.0, 49.0],
                      [-117.0, 49.0],
                      [-117.0, 45.0],
                      [-125.0, 45.0],
                      [-125.0, 49.0]
                  ]
              ]
          ]
        }'

This is the same query, but using '-l'/'--lat-lng' option:

    $ fccsmap --log-level=DEBUG -l 45.0:49.0,-125.0:-117.0

Here's one that looks up fuelbeds under too polygon regions

 $ fccsmap --log-level=DEBUG -g '{
      "type": "MultiPolygon",
      "coordinates": [
        [
          [
            [-121.4522115, 47.4316976],
            [-121.3990506, 47.4316976],
            [-121.3990506, 47.4099293],
            [-121.4522115, 47.4099293],
            [-121.4522115, 47.4316976]
          ]
        ],
        [
          [
            [-120.4522115, 47.4316976],
            [-120.3990506, 47.4316976],
            [-120.3990506, 47.4099293],
            [-120.4522115, 47.4099293],
            [-120.4522115, 47.4316976]
          ]
        ]
      ]
    }'

Here's an example that looks up the fuelbed information at a specific
location

 $ fccsmap --log-level=DEBUG -l 47.0,-121.0
