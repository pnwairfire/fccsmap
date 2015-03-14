"""lookup.py:
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import os

from osgeo import gdal
from osgeo import ogr
from osgeo import osr

__all__ = [
    'FccsGrid'
]

gdal.UseExceptions()
gdal.AllRegister()
ogr.RegisterAll()


class FccsGrid(object):
    """

    To inspect the FCCS loopup map netCDF files, use the following

    $ ferret
    yes? set mem/size=200
    yes? use fccs_fuelload.nc
    yes? show data
    yes? FILL/level=(0,1000,10) FCCS_FUELLOADING
    """

    def __init__(self, **options):

        # TODO: make sure there is indeed only one band
        filename = options.get('fccs_fuelload_file') or (
            os.path.dirname(__file__) + '/data/fccs_fuelload.nc')
        filename = "NETCDF:%s:FCCS_FuelLoading" % (filename)
        self.gridfile = gdal.Open(filename)
        self.metadata = self.gridfile.GetMetadata()

        for k, v in self.metadata.iteritems():
            if k.startswith("NC_GLOBAL#"):
                key = k[10:]
                if not hasattr(self, key):
                    try:
                        setattr(self, key, v)
                    except:
                        pass

