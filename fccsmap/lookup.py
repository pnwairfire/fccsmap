"""lookup.py:
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import json
from osgeo import ogr

from .fccsgrid import FccsGrid

__all__ = [
    'FccsLookUp'
]

class FccsLookUp(object):

    def __init__(self, **options):
        self.fccs_grid = FccsGrid(**options).load()


    ##
    ## Public Interface
    ##

    def look_up(self, geo_data):
        """Looks up FCCS fuelbed information within a region defined by
        multipolygon region
        Arguments
         - geo_data -- json formatted (or already loaded)

        Expected format of geo_data:

            {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [-84.5212, 32.3082],
                            [-84.5215, 32.3069],
                            [-84.5211, 32.3095],
                            [-84.5212, 32.3082]
                        ]
                    ],
                    [
                        [
                            [-84.5042, 32.3242],
                            [-84.5045, 32.3228],
                            [-84.5041, 32.3255],
                            [-84.5042, 32.3242]
                        ]
                    ]
                ]
            }
        """
        #multipolygon = self._create_polygon(multipolygon_coordinates)
        if hasattr(geo_data, 'has_key'):
            geo_data = json.dumps(geo_data)
        multipolygon = ogr.CreateGeometryFromJson(geo_data)
        return multipolygon.ExportToWkt()  # TEST!

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

