# fccsmap

This package supports the look-up of FCCS fuelbed information by lat/lng or
vector geo spatial data.

## Dependencies

Whether cloning the repo or installing with pip, you'll first need to
manually install gdal, proj, and netcdf, which fccsmap depends on.  These
instructions assume you already have python and pip installed, as well as
C and C++ compilers, etc.

### Mac

On a mac, using [Homebrew](http://brew.sh/):

    brew install homebrew/science/netcdf
    brew install proj
    brew install gdal --with-netcdf --enable-unsupported

Note that the '--with-netcdf' option is required to build gdal with the
netCDF driver. See http://trac.osgeo.org/gdal/wiki/NetCDF for more information.

Additionally, you'll need the gdal python bindings.  These used to be
baked into setup.py, but the version available for install depends
on your platform.

    gdal-config --version
    pip install gdal==`gdal-config --version`

### Ubuntu, 12.04 LTS (precise )

First update

    sudo apt-get update
    #sudo apt-get upgrade

If you don't have python and pip installed:

    sudo apt-get install -y python python-dev python-pip
    sudo pip install --upgrade pip

Install libnetcdf and libproj

    sudo apt-get install -y libnetcdf-dev proj

Install numpy and gdal.

    sudo pip install numpy==1.8.0
    sudo apt-get install -y libgdal1-1.7.0
    sudo pip install gdal==1.7.0

On ubuntu, you may need to install gdal manually

    sudo apt-get install checkinstall
    cd /usr/local/src
    sudo wget http://download.osgeo.org/gdal/gdal-1.7.3.tar.gz
    sudo tar xvfz gdal-1.7.3.tar.gz
    cd gdal-1.7.3
    sudo ./configure --with-python --prefix=/usr/local
    sudo make
    sudo checkinstall  #sudo make install
    sudo ldconfig

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

    pip install --no-binary gdal --trusted-host pypi.smoke.airfire.org -r requirements.txt

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
    pip install --no-binary :all: gdal==1.11.2

If this doesn't work, uninstall gdal, and then install it manually:

    pip uninstall -y GDAL
    wget https://pypi.python.org/packages/source/G/GDAL/GDAL-1.11.2.tar.gz
    tar xzf GDAL-1.11.2.tar.gz
    cd GDAL-1.11.2
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
    py.test test/fccsmap/

You can also use the ```--collect-only``` option to see a list of all tests.

    py.test --collect-only

See [pytest](http://pytest.org/latest/getting-started.html#getstarted) for more information about

## Installing

First install the non-python dependencies (mentioned above).

### Installing With pip

First, install pip (with sudo if necessary):

    apt-get install python-pip

Then, to install, for example, version 0.2.1, use the following (with
sudo if necessary):

    pip install --no-binary gdal --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple fccsmap==0.2.1

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

Here's one that looks up fuelbeds under two polygon regions

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

## Docker

### Installing Docker

See https://docs.docker.com/engine/installation/ for platform specific
installation instructions.

### Building Docker Image

#### Mac OSX

##### Starting Docker deamon

On a Mac, the docker daemon runs inside a Linux VM. The first time
you use docker, you'll need to create a vm:

    docker-machine create --driver virtualbox default

Check that it was created:

    docker-machine ls

Set env vars so that your docker knows how to find the docker host:

    eval "$(docker-machine env default)"

#### Ubuntu

...TODO: fill in insructions...


### Build Bluesky Docker Image from Docfile

    docker build -t fccsmap .

### Run in Docker

If you run the image without a command, i.e.:

    docker run fccsmap

it will output the fccsmap help image.  To fccsmap with input, use
something like the following:

    docker run fccsmap fccsmap --log-level=DEBUG -l 45.0:49.0,-125.0:-117.0
