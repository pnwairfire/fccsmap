"""fccsmap.lookup

For debugging purposes, you can inspect the fccs NetCDF files directly
with ferret. See http://ferret.pmel.noaa.gov/Ferret/ to obtain it.
Tutorial: http://ferret.pmel.noaa.gov/Ferret/documentation/ferret-tutorial.
Very simple usage:

  $ cd /path/to/fccsmap/repo/fccsmap/data/
  $ ferret
  yes? use fccs2_fuelload.nc
  yes? set mem/size=200
  yes? shade/level=(0,900,10) band1
"""

__author__      = "Joel Dubowy"

import json
import logging
import math
import os
import re
from collections import defaultdict

from osgeo import gdal
from pyproj import Proj
from rasterstats import zonal_stats
from shapely import ops, geometry

__all__ = [
    'FccsLookUp'
]

class FccsLookUp(object):

    FUEL_LOAD_NCS = {
        'fccs1': {
            'file': os.path.dirname(__file__) + '/data/fccs_fuelload.nc',
            'param': 'FCCS_FuelLoading',
            'grid_resolution': 1
        },
        'fccs2': {
            'file': os.path.dirname(__file__) + '/data/fccs2_fuelload.nc',
            'param': 'Band1',
            'grid_resolution': 1
        },
        'ak': {
            'file': os.path.dirname(__file__) + '/data/FCCS_Alaska.nc',
            'param': 'Band1',
            'grid_resolution': 1
        }
    }

    IGNORED_PERCENT_RESAMPLING_THRESHOLD = 99.9  # instead of 100.0, to account for rounding errors
    IGNORED_FUELBEDS = ('0', '900')

    # OPTIONS_DOC_STRING used by Constructor docstring as well as
    # script helpstring
    OPTIONS_STRING = """
         - is_alaska -- Whether or not location is in Alaska; boolean
         - fccs_version -- '1' or '2'
         - fccs_fuelload_file -- NetCDF file containing FCCS lookup map
         - fccs_fuelload_param -- name of variable in NetCDF file
         - grid_resolution -- length of grid cells in km
         - ignored_fuelbeds -- fuelbeds to ignore
         - ignored_percent_resampling_threshold -- percentage of ignored
            fuelbeds which should trigger resampling in larger area; only
            plays a part in Point and MultiPoint look-ups
         - no_sampling -- don't sample surrounding area for Point
            and MultiPoint geometries
         - use_all_grid_cells -- Consider FCCS map grid cells entirely within
            the area of interest as well as cells partially outside of the area.
            (The default behavior is to ignore partial cells, unless there are no
            fully included cells, in which case parials are used.)
    """

    def __init__(self, **options):
        """Constructor

        Valid options:

        {}

        TODO: determine grid_resolution from NetCDF file
        """.format(self.OPTIONS_STRING)

        # TODO: determine which combinations of file/param/version can be
        #   specified and raise errors when appropriate (including invalid
        #   nonexisting versions)

        is_alaska = options.get('is_alaska', False)
        fccs_version = options.get('fccs_version') or '2'
        fuel_load_key = 'ak' if is_alaska else 'fccs%s'%(fccs_version)
        logging.debug('fuel load key: %s', fuel_load_key)

        for k in ('file', 'param', 'grid_resolution'):
            v = (options.get('fccs_fuelload_{}'.format(k))
                or self.FUEL_LOAD_NCS[fuel_load_key][k])
            setattr(self, 'filename' if k=='file' else k, v)

        self.gridfile_specifier = "NETCDF:%s:%s" % (self.filename, self.param)
        self._initialize_projector()

        self._ignored_fuelbeds = options.get(
            'ignored_fuelbeds', self.IGNORED_FUELBEDS)
        self._ignored_percentre_sampling_threshold = options.get(
            'ignored_percent_resampling_threshold',
            self.IGNORED_PERCENT_RESAMPLING_THRESHOLD)
        self._no_sampling = options.get('no_sampling', False)
        self._use_all_grid_cells = options.get('use_all_grid_cells', False)

    ##
    ## Public Interface
    ##

    def look_up(self, geo_data):
        """Looks up FCCS fuelbed information within a region defined by
        multipolygon region

        Arguments
         - geo_data -- vector data, json formatted (or already loaded)

        Examples of valid geo_data format:

          MultiPoint:

            {
                "type": "MultiPoint",
                "coordinates": [
                    [-121.4522115, 47.4316976],
                    [-120.0, 48.0]
                ]
            }

          MultiPolygon:

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

        if not self._no_sampling and geo_data["type"] in (
                'Point', 'MultiPoint'):
            logging.debug("Sampling 1 * grid resoluation")
            new_geo_data = self._transform_points(geo_data,
                self.grid_resolution)
            stats = self._look_up(new_geo_data)

            if self._has_high_percent_of_ignored(stats):
                logging.debug("Resampling 3 * grid resoluation")
                new_geo_data = self._transform_points(geo_data,
                    3*self.grid_resolution)
                stats = self._look_up(new_geo_data)
                # at this point, if all water, we'll stick with it

            stats['sampled_grid_cells'] = stats.pop('grid_cells')
            stats['sampled_area'] = stats.pop('area')

        else:
            stats = self._look_up(geo_data)

        stats = self._remove_ignored(stats)
        stats = self._remove_insignificant(stats)

        return stats

    ##
    ## Helper methods
    ##

    LAT_0_EXTRACTOR = re.compile('PARAMETER\["latitude_of_center",([^]]+)\]')

    def _initialize_projector(self):
        self.gridfile = gdal.Open(self.gridfile_specifier)
        metadata = self.gridfile.GetMetadata()
        proj_type = metadata['%s#grid_mapping' % (self.param)]

        if proj_type == 'lambert_conformal_conic':
            self.projector = Proj(
                proj='lcc',
                #datum='NAD83', # TODO: read this self.gridfile
                lat_0=metadata['#'.join([proj_type,'latitude_of_projection_origin'])],
                lat_1=metadata['#'.join([proj_type,'standard_parallel_1'])],
                lat_2=metadata['#'.join([proj_type,'standard_parallel_2'])],
                lon_0=metadata['#'.join([proj_type,'central_meridian'])]
            )
        elif proj_type == 'albers_conical_equal_area':
            # Parameters to set:
            #  - proj -- 'aea'
            #  - lat_1 -- Latitude of first standard parallel
            #  - lat_2 -- Latitude of second standard parallel
            #  - lat_0 -- Latitude of false origin
            #  - lon_0 -- Longitude of false origin
            #  - x_0 -- Easting of false origin
            #  - y_0 -- Northing of false origin

            lat_1 = float(metadata['#'.join([proj_type,'standard_parallel_1'])])
            lat_2 = float(metadata['#'.join([proj_type,'standard_parallel_2'])])

            # To get the lat_0 parameter, we need to extract it from the
            # 'spatial_ref' metadata field; it looks something like this:
            #   'PROJCS["NAD_1983_Albers",GEOGCS["NAD83",DATUM["North_American_Datum_1983",SPHEROID["GRS 1980",6378137,298.2572221010002,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6269"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4269"]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["standard_parallel_1",29.5],PARAMETER["standard_parallel_2",45.5],PARAMETER["latitude_of_center",23],PARAMETER["longitude_of_center",-96],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'
            # This is a bit hacky, but it works
            spacial_ref = metadata['#'.join([proj_type,'spatial_ref'])]
            m = self.LAT_0_EXTRACTOR.search(spacial_ref)
            if not m:
                raise RuntimeError("Failed to determine latitude of false origin")
            lat_0 = float(m.group(1))
            lon_0 = float(metadata['#'.join([proj_type,'longitude_of_central_meridian'])])

            false_easting = metadata['#'.join([proj_type, 'false_easting'])]
            false_northing = metadata['#'.join([proj_type, 'false_northing'])]
            logging.debug('false_easting, false_northing: %s, %s',
                false_easting, false_northing)
            x_0 = int(float(false_easting))
            y_0 = int(float(false_northing))

            self.projector = Proj(proj='aea', lat_1=lat_1, lat_2=lat_2,
                lat_0=lat_0, lon_0=lon_0, x_0=x_0, y_0=y_0)
        else:
            raise ValueError("Grid mapping projection not supported: %s" % (
                metadata['%s#grid_mapping' % (self.param)]
            ))

    KM_PER_DEG_LAT = 111.0
    KM_PER_DEG_LNG_AT_EQUATOR = 111.321

    def _transform_points(self, geo_data, radius_in_km):
        coordinates = (geo_data['coordinates']
            if geo_data['type'] == 'MultiPoint'
            else [geo_data['coordinates']])

        # delta_lat and and delta_lng_factor could be computed once
        # per instance, but we'd still have to multiple by some factor
        # given the size of the sphere of influence, and it could make
        # code more complicated for what would probably be not much
        # performance gain.
        # TODO: benchmark to confirm the comment above?
        delta_lat = radius_in_km / self.KM_PER_DEG_LAT
        delta_lng_factor = (radius_in_km / self.KM_PER_DEG_LNG_AT_EQUATOR)

        new_geo_data = {
          "type": "MultiPolygon",
          "coordinates": []
        }
        for c in coordinates:
            delta_lng = delta_lng_factor / math.cos((math.pi*c[1])/180.0)
            new_geo_data["coordinates"].append([[
                [c[0]-delta_lng, c[1]-delta_lat],
                [c[0]-delta_lng, c[1]+delta_lat],
                [c[0]+delta_lng, c[1]+delta_lat],
                [c[0]+delta_lng, c[1]-delta_lat],
            ]])

        return new_geo_data

    def _look_up(self, geo_data):
        s = geometry.shape(geo_data)
        s = ops.transform(self.projector, s)

        def counts(x):
            # We'll ignore the mask (i.e. consider partial cells) if
            # configured to do so or if the mask is all true values
            # (i.e. all cells are partial)
            ignore_mask = self._use_all_grid_cells or not any([
                not val for subarray in x.mask  for val in subarray
            ])
            counts = defaultdict(lambda: 0)
            for i in range(len(x.data)):
                for j in range(len(x.data[i])):
                    if (ignore_mask or not x.mask[i][j]) and x.data[i][j] >= 0:
                        counts[x.data[i][j]] += 1
            return dict(counts)

        stats = zonal_stats(s, self.gridfile_specifier,
            add_stats={'counts':counts})
        # TODO: make sure area units are correct and properly translated
        # to real geographical area; read them from nc file
        # TODO: read and include grid cell size from nc file
        final_stats = self._compute_percentages(stats)
        final_stats.update(area=s.area, units='m^2')
        return final_stats

    def _has_high_percent_of_ignored(self, stats):
        return (self._compute_total_percent_ignored(stats) >=
            self._ignored_percentre_sampling_threshold)

    def _compute_total_percent_ignored(self, stats):
        return sum([
            stats.get('fuelbeds', {}).get(fccs_id, {}).get('percent') or 0
                for fccs_id in self._ignored_fuelbeds
        ])

    def _compute_percentages(self, stats):
        total_counts = defaultdict(lambda: 0)
        for stat_set in stats:
            for fccs_id, count in list(stat_set.get('counts', {}).items()):
                total_counts[fccs_id] += count
        total = sum(total_counts.values())
        return {
            'grid_cells': total,
            'fuelbeds': {
                str(k): {
                    'percent': 100.0 * float(v)/float(total), 'grid_cells': v
                } for k,v in list(total_counts.items())
            }
        }

    def _remove_ignored(self, stats):
        """Removes ignored fuelbeds and readjusts percentages so that they
        add up to 100.
        """
        # TODO: don't recompute total ignored if it was already computed,
        #   i.e. for Point or MultiPoint
        total_percent_ignored = self._compute_total_percent_ignored(stats)

        if total_percent_ignored == 100.0:
            stats['fuelbeds'] = {}

        elif total_percent_ignored > 0.0:
            stats = self._readjust_percentages(stats, total_percent_ignored)

        return stats

    INSIGNIFICANCE_THRESHOLD = 10.0

    def _remove_insignificant(self, stats):
        """Removes fuelbeds that make up an insignificant fraction of the
        total fuelbed composition (i.e. those that cumulatively make up
        less than INSIGNIFICANCE_THRESHOLD), and readjust percentages to that
        they add up to 100.
        """
        sorted_fuelbeds = sorted(stats.get('fuelbeds', {}).items(),
            key=lambda e: e[1]['percent'])
        total_percentage_removed = 0.0
        for fccs_id, f_dict in sorted_fuelbeds:
            if (total_percentage_removed + f_dict['percent']
                    < self.INSIGNIFICANCE_THRESHOLD):
                total_percentage_removed += f_dict['percent']
                stats['fuelbeds'].pop(fccs_id)

        if total_percentage_removed >= 0.0:
            stats = self._readjust_percentages(stats, total_percentage_removed)

        return stats

    def _readjust_percentages(self, stats, missing_percentage):
        """Readjust fuelbed percentages so that they add up to 100%

        Note: missing_percentage could easily be computed here, but
        it's already computed before each call to this method, so it's
        passed in to avoid redundant computation.
        """
        if stats.get('fuelbeds') and missing_percentage > 0:
            adjustment_factor = 100.0 / (100.0 - missing_percentage)
            # cast to list so that we can call pop within loop
            for fccs_id in list(stats.get('fuelbeds', {})):
                if fccs_id in self._ignored_fuelbeds:
                    stats['fuelbeds'].pop(fccs_id)
                else:
                    p = stats['fuelbeds'][fccs_id]['percent'] * adjustment_factor
                    stats['fuelbeds'][fccs_id]['percent'] = p

        return stats
