"""lookup.py:
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import json
import logging
import os
from collections import defaultdict

from osgeo import gdal
from pyproj import Proj
from rasterstats import zonal_stats
from shapely import ops, geometry

__all__ = [
    'FccsLookUp'
]

FUEL_LOAD_NCS = {
    'fccs1': {
        'file': os.path.dirname(__file__) + '/data/fccs_fuelload.nc',
        'param': 'FCCS_FuelLoading'
    },
    'fccs2': {
        'file': os.path.dirname(__file__) + '/data/fccs2_fuelload.nc',
        'param': 'Band1'
    },
    'ak': {
        'file': os.path.dirname(__file__) + '/data/FCCS_Alaska.nc',
        'param': 'Band1'
    }
}


class FccsLookUp(object):

    def __init__(self, **options):

        # TODO: determine which combinations of file/param/version can be
        # specified and raise errors when appropriate

        is_alaska = options.get('is_alaska', False)
        fccs_version = options.get('fccs_version', 2)
        fuel_load_key = 'ak' if is_alaska else 'fccs%s'%(fccs_version)
        logging.debug('fuel load key: %s', fuel_load_key)

        self.filename = options.get('fccs_fuelload_file') or FUEL_LOAD_NCS[fuel_load_key]['file']
        self.param = options.get('fccs_fuelload_param') or FUEL_LOAD_NCS[fuel_load_key]['param']
        self.gridfile_specifier = "NETCDF:%s:%s" % (self.filename, self.param)
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
                        # Note: if x.data[i][j] < 0, it's up
                        # to calling code to deal with it
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
        metadata = self.gridfile.GetMetadata()

        if metadata['%s#grid_mapping' % (self.param)] == 'lambert_conformal_conic':
            self.projector = Proj(
                proj='lcc',
                #datum='NAD83', # TODO: read this self.gridfile
                lat_0=metadata['lambert_conformal_conic#latitude_of_projection_origin'],
                lat_1=metadata['lambert_conformal_conic#standard_parallel_1'],
                lat_2=metadata['lambert_conformal_conic#standard_parallel_2'],
                lon_0=metadata['lambert_conformal_conic#central_meridian']
            )
        else:
            raise ValueError("Grid mapping projection not supported: %s" % (
                metadata['%s#grid_mapping' % (self.param)]
            ))


    def _compute_percentages(self, stats):
        total_counts = defaultdict(lambda: 0)
        for stat_set in stats:
            for fccs_id, count in stat_set['counts'].items():
                total_counts[fccs_id] += count
        total = float(sum(total_counts.values()))
        return {str(k):float(v)/total for k,v in total_counts.items()}
