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
    sudo apt-get install python-gdal
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

Then, to install, for example, v0.1.3, use the following:

    sudo pip install git+https://github.com/pnwairfire/fccsmap@v0.1.3

If you get an error like    ```AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex```, it means you need in upgrade pip.  One way to do so is with the following:

    pip install --upgrade pip

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
