"""lookup.py:
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import json
import os
from collections import defaultdict

from pyproj import Proj
from rasterstats import zonal_stats
from shapely.geometry import shape

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

        if hasattr(geo_data, 'capitalize'):
            geo_data = json.loads(geo_data)
        self._project(geo_data)
        s = shape(geo_data)

        def counts(x):
            counts = defaultdict(lambda: 0)
            for i in xrange(len(x.data)):
                for j in xrange(len(x.data[i])):
                    if not x.mask[i][j]:
                        counts[x.data[i][j]] += 1
            return dict(counts)

        stats = zonal_stats(s, self.gridfile_specifier,
            add_stats={'counts':counts})
        return self._compute_percentages(stats)

    NC_PROJECTION = 'lcc' # TODO: read this from nc file
    NC_DATUM = 'NAD83' # TODO: read this from nc file

    ##
    ## Helper methods
    ##

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

    def _compute_percentages(self, stats):
        total_counts = defaultdict(lambda: 0)
        for stat_set in stats:
            for fccs_id, count in stat_set['counts'].items():
                total_counts[fccs_id] += count
        total = float(sum(total_counts.values()))
        return {str(k):float(v)/total for k,v in total_counts.items()}
