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

def InvGeoTransform(gt_in):
    # Based on InvGeoTransform() by Frank Warmerdam

    # Compute determinate (assumes 3rd row that is [1 0 0])
    det = gt_in[1] * gt_in[5] - gt_in[2] * gt_in[4]
    if abs(det) < 0.000000000000001:
        raise Exception("Inverse geotransform failed")

    inv_det = 1.0 / det
    # Compute adjoint, and divide by determinate
    return [
        ( gt_in[2] * gt_in[3] - gt_in[0] * gt_in[5]) * inv_det,
        gt_in[5] * inv_det,
        -gt_in[2] * inv_det,
        (-gt_in[1] * gt_in[3] + gt_in[0] * gt_in[4]) * inv_det,
        -gt_in[4] * inv_det,
        gt_in[1] * inv_det
    ]

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

        # TODO: check if
        #   "NC_GLOBAL#IOAPI_VERSION" in self.metadata and
        #   "NC_GLOBAL#Conventions" not in self.metadata:
        #  IF so, then need to use alternate logic (see bluesky.kernel.grid)

        # The elements, by index, in self.geotransform are
        #  0: min x
        #  1: cell_size_x
        #  2: skew x
        #  3: min y
        #  4: skey y
        #  5: cell size y
        self.geotransform = self.gridfile.GetGeoTransform()
        self.spatialref = osr.SpatialReference(self.gridfile.GetProjection())
        self.invtransform = InvGeoTransform(self.geotransform)
        self.sizeX = self.gridfile.RasterXSize
        self.sizeY = self.gridfile.RasterYSize
        latlon = osr.SpatialReference()
        latlon.SetWellKnownGeogCS("WGS84")
        self.LL2XY = osr.CoordinateTransformation(latlon, self.spatialref)
        self.XY2LL = osr.CoordinateTransformation(self.spatialref, latlon)

        # self.variables = {}
        # for dsname, dsdesc in self.gridfile.GetSubDatasets():
        #     varname = dsname.split(':')[2]
        #     self.variables[varname] = GridFile(dsname)

        # self.__currentband = None
        # self.__currentgrid = None
        # if self.gridfile.RasterCount == 1:
        #     band = 1
        # if band:
        #     self.getBand(band)

        self.rb = self.gridfile.GetRasterBand(1)
        self.noDataValue = self.rb.GetNoDataValue()
        self.sizeX = self.rb.XSize
        self.sizeY = self.rb.YSize
        self.dataType = gdal.GetDataTypeName(self.rb.DataType)

        self.data = self.rb.ReadAsArray(0, 0, self.sizeX, self.sizeY, self.sizeX, self.sizeY)
        #import pdb;pdb.set_trace()
        foo =1

    ##
    ## Inforation about amount of data
    ##

    def size(self):
        return (self.gridfile.RasterXSize, self.gridfile.RasterYSize)

    def __len__(self):
        return self.gridfile.RasterCount

    def __nonzero__(self):
        # TODO: check this
        return self.gridfile.RasterCount != 0

    ##
    ## Accessing data
    ##

    def __call__(self, x, y):
        return self.at_index(x, y)

    def __getitem__(self, indices):
        x, y = [int(x) for x in indices]
        return self.at_index(x, y)

    def at_index(x, y):
        # if x < 0 or x >= self.sizeX:
        #     raise ValueError("X coordinate out of range")
        # if y < 0 or y >= self.sizeY:
        #     raise ValueError("Y coordinate out of range")
        # value = self.data[y, x]
        # if hasattr(value, "toscalar"):
        #     value = value.toscalar()
        # elif self.dataType.startswith("Float"):
        #     value = float(value)
        # else:
        #     value = int(value)
        # if value == self.noDataValue:
        #     return None
        # return value
        pass

    def at_lat_lng(lat, lng):
        x, y, z = self.LL2XY.TransformPoint(lat, lng)
        x, y = self.get_closest_cell(x, y)
        return self.at_index(x, y)

    def within_polygon(coordinate_vector_data):
        raise NotImplementedError()

    def get_closest_cell(self, x, y):
        gt_out = self.invtransform
        gridX = (gt_out[0] + (x * gt_out[1]) + (y * gt_out[2])) - 0.5
        gridY = (gt_out[3] + (x * gt_out[4]) + (y * gt_out[5])) - 0.5
        closestX = int(round(gridX))
        closestY = int(round(gridY))
        return (closestX, closestY)


    def getValueAt(self, latitude, longitude, band=None, param=None):
        if param:
            return self.variables[param].getValueAt(latitude, longitude, band)
        if not band:
            band = self.__currentband
        x, y = self.getCellByLatLon(latitude, longitude)
        grid = self.getBand(band)
        return grid.getValue(x, y)

    def getCellCoord(self, px, py):
        x = int(px) + 0.5;
        geoX = self.geotransform[0] + (x * self.geotransform[1]) + (y * self.geotransform[2])
        geoY = self.geotransform[3] + (x * self.geotransform[4]) + (y * self.geotransform[5])
        return (geoX, geoY)

    def getCellByLatLon(self, latitude, longitude):
        pass

    def getCoordsByLatLon(self, latitude, longitude):
        x, y, z = self.LL2XY.TransformPoint(longitude, latitude)
        return (x, y)

    def getLatLonByCell(self, x, y):
        geoX, geoY = self.getCellCoord(x, y)
        longitude, latitude, z = self.XY2LL.TransformPoint(geoX, geoY)
        return (latitude, longitude)

    def close(self):
        del self.gridfile
        del self.variables
        del self.metadata
        del self.spatialref
        del self.LL2XY
        del self.XY2LL
        del self.__currentgrid
