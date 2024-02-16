"""fccsmap.lookup

For debugging purposes, you can inspect the fccs NetCDF files directly
with ferret. See http://ferret.pmel.noaa.gov/Ferret/ to obtain it.
Tutorial: http://ferret.pmel.noaa.gov/Ferret/documentation/ferret-tutorials.
Very simple usage:

  $ cd /path/to/fccsmap/repo/fccsmap/data/
  $ ferret
  yes? use fccs2_fuelload.nc
  yes? set mem/size=200
  yes? shade/level=(0,900,10) band1
"""

__author__      = "Joel Dubowy"

import logging
import os
import re
from collections import defaultdict

import geopandas
import rioxarray
from osgeo import gdal
from pyproj import Proj
from rasterstats import zonal_stats
from shapely import ops, geometry

from . import BaseLookUp

__all__ = [
    'FccsLookUp'
]

class FccsLookUp(BaseLookUp):

    FUEL_LOAD_NCS = {
        'fccs1': {
            'file': os.path.dirname(__file__) + '/data/fccs_fuelload.nc',
            'sampling_radius_km': 1
        },
        'fccs2': {
            'file': os.path.dirname(__file__) + '/data/fccs2_fuelload.nc',
            'sampling_radius_km': 1
        },
        'ak': {
            'file': os.path.dirname(__file__) + '/data/FCCS_Alaska.nc',
            'sampling_radius_km': 1
        },
        'ca': {
            'file': os.path.dirname(__file__) + '/data/fccs_canada.nc',
            'sampling_radius_km': 1
        }
    }

    # OPTIONS_DOC_STRING used by Constructor docstring as well as
    # script helpstring
    ADDITIONAL_OPTIONS_STRING = """
         - is_alaska -- Whether or not location is in Alaska; boolean
         - is_canada -- Whether or not location is in Canada; boolean
         - fccs_version -- '1' or '2'
         - fccs_fuelload_file -- raster file containing FCCS lookup map
         - sampling_radius_km -- length of grid cells in km
    """

    def __init__(self, **options):
        """Constructor

        Valid options:

        {}

        TODO: determine grid resolution from NetCDF file and set sampling radius to it
        """.format(self.OPTIONS_STRING + self.ADDITIONAL_OPTIONS_STRING)

        # TODO: determine which combinations of file/param/version can be
        #   specified and raise errors when appropriate (including invalid
        #   nonexisting versions)

        if options.get('is_alaska', False):
            fuel_load_key = 'ak'
        elif options.get('is_canada', False):
            fuel_load_key = 'ca'
        else:
            fuel_load_key = f"fccs{options.get('fccs_version') or '2'}"
        logging.debug('fuel load key: %s', fuel_load_key)

        # TODO: support loading tif (or other?) file formats

        for k in ('file', 'sampling_radius_km'):
            attr = '_filename' if k=='file' else f"_{k}"
            val = (options.get('fccs_fuelload_{}'.format(k))
                or self.FUEL_LOAD_NCS[fuel_load_key][k])
            logging.debug(f"Setting {attr} to {val}")
            setattr(self, attr, val)

        super().__init__(**options)

    ##
    ## Helper methods
    ##

    def _look_up(self, geo_data):
        # set crs
        raster = rioxarray.open_rasterio(self._filename)
        self._crs = raster[0].rio.crs

        geo_data_df = self._create_geo_data_df(geo_data)
        return self._look_up_in_file(geo_data_df, self._filename)
