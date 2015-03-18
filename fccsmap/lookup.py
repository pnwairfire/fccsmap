"""lookup.py:
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import json
import os
from collections import defaultdict

from osgeo import gdal
from pyproj import Proj
from rasterstats import zonal_stats
from shapely import ops, geometry

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
        self._initialize_projector()
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
        s = geometry.shape(geo_data)
        s = ops.transform(self.projector, s)

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

    ##
    ## Helper methods
    ##

    def _initialize_projector(self):
        self.gridfile = gdal.Open(self.gridfile_specifier)
        # TODO: inspect gridfile to determine type projection used and create
        # correct projector (lcc, albers_conical_equal_area, etc)
        self.nc_datum = 'NAD83' # TODO: read this self.gridfile
        self.nc_projection = 'lcc' # TODO: read/determine this self.gridfile
        self.xcenter = 40 # TODO: read this self.gridfile
        self.ycenter = -100 # TODO: read this self.gridfile
        self.reference_parallel_a=33
        self.reference_parallel_b=45

        self.projector = Proj(
            proj=self.nc_projection,
            datum=self.nc_datum,
            lat_0=self.xcenter,
            lat_1=self.reference_parallel_a,
            lat_2=self.reference_parallel_b,
            lon_0=self.ycenter
        )

    def _compute_percentages(self, stats):
        total_counts = defaultdict(lambda: 0)
        for stat_set in stats:
            for fccs_id, count in stat_set['counts'].items():
                total_counts[fccs_id] += count
        total = float(sum(total_counts.values()))
        return {str(k):float(v)/total for k,v in total_counts.items()}
