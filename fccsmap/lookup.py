"""lookup.py:
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import json
import os

from osgeo import ogr
from pyproj import Proj
from rasterstats import zonal_stats
from shapely.geometry import shape

from .fccsgrid import FccsGrid

__all__ = [
    'FccsLookUp'
]

FUEL_LOAD_NC = os.path.dirname(__file__) + '/data/fccs_fuelload.nc'
AK_FUEL_LOAD_NC = os.path.dirname(__file__) + '/data/FCCS_Alaska.nc'

class FccsLookUp(object):

    def __init__(self, **options):
        #self.fccs_grid = FccsGrid(**options)
        filename = options.get('fccs_fuelload_file')
        if not filename:
             filename = AK_FUEL_LOAD_NC if options.get('is_alaska') else FUEL_LOAD_NC
        self.gridfile_specifier = "NETCDF:%s:FCCS_FuelLoading" % (filename)

    ##
    ## Public Interface
    ##

    def look_up(self, geo_data):
        """Looks up FCCS fuelbed information within a region defined by
        multipolygon region

        Arguments
         - geo_data -- vector data, json formatted (or already loaded)

        Expected format of geo_data:

            {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [-121.6458395, 47.8211024],
                            [-121.0439946, 47.8211024],
                            [-121.0439946, 47.3861258],
                            [-121.6458395, 47.3861258],
                            [-121.6458395, 47.8211024]
                        ]
                    ]
                ]
            }
        """

        # TEST
        # geo_data = {
        #         "type": "MultiPolygon",
        #         "coordinates": [
        #             [
        #                 [
        #                     [-190000, 1320000],
        #                     [-170000, 1330000],
        #                     [-170000, 1310000],
        #                     [-190000, 1310000],
        #                     [-190000, 1320000]
        #                 ]
        #             ]
        #         ]
        #     }


        #multipolygon = self._create_polygon(multipolygon_coordinates)
        if hasattr(geo_data, 'capitalize'):
            geo_data = json.loads(geo_data)
        self._project(geo_data)
        #import pdb;pdb.set_trace()
        s = shape(geo_data)

        def foo(x):
            # TODO: implement
            #import pdb;pdb.set_trace()
            return 0

        stats = zonal_stats(s, self.gridfile_specifier, add_stats={'foo':foo})
        return stats

    NC_PROJECTION = 'lcc' # TODO: read this from nc file
    NC_DATUM = 'NAD83' # TODO: read this from nc file

    def _project(self, geo_data):
        p = Proj(
            proj=self.NC_PROJECTION,
            datum=self.NC_DATUM,
            lat_0=40, # TODO: read this from nc file
            lat_1=33, # TODO: read this from nc file
            lat_2=45, # TODO: read this from nc file
            lon_0=-100 # TODO: read this from nc file
        )
        #p = Proj(init='epsg:26915')
        for polygon_coordinates in geo_data["coordinates"]:
            for outer in polygon_coordinates:
                for coordinates in outer:
                    projected = p(*coordinates)
                    coordinates[0] = projected[0]
                    coordinates[1] = projected[1]
                    coordinates.append(0)
                    # TODO: set the coordinates to thep projected


    ##
    ## Helper methods
    ##

    # def _create_polygon(self, multipolygon_coordinates):
    #     multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)
    #     for polygon_coordinates in multipolygon_coordinates:
    #         polygon = ogr.Geometry(ogr.wkbPolygon) # Is this the correct type?
    #         # TODO: figure out why array of coordinates is nested within an
    #         # array of size 1 for each polygon
    #         for coordinate in polygon_coordinates[0]:
    #             point = ogr.Geometry(ogr.wkbPoint)
    #             point.AddPoint(*coordinate)
    #             polygon.AddGeometry(point)

    #         multipolygon.AddGeometry(polygon)
    #     return multipolygon

