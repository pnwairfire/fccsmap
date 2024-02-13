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
        },
        'ca': {
            'file': os.path.dirname(__file__) + '/data/fccs_canada.nc',
            'param': 'Band1',
            'grid_resolution': 1
        }
    }

    # OPTIONS_DOC_STRING used by Constructor docstring as well as
    # script helpstring
    ADDITIONAL_OPTIONS_STRING = """
         - is_alaska -- Whether or not location is in Alaska; boolean
         - is_canada -- Whether or not location is in Canada; boolean
         - fccs_version -- '1' or '2'
         - fccs_fuelload_file -- NetCDF file containing FCCS lookup map
         - fccs_fuelload_param -- name of variable in NetCDF file
         - grid_resolution -- length of grid cells in km
    """

    def __init__(self, **options):
        """Constructor

        Valid options:

        {}

        TODO: determine grid_resolution from NetCDF file
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

        for k in ('file', 'param', 'grid_resolution'):
            attr = 'filename' if k=='file' else k
            val = (options.get('fccs_fuelload_{}'.format(k))
                or self.FUEL_LOAD_NCS[fuel_load_key][k])
            logging.debug(f"Setting {attr} to {val}")
            setattr(self, attr, val)

        self.gridfile_specifier = "NETCDF:%s:%s" % (self.filename, self.param)
        self._initialize_projector()

        super().__init__(**options)


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
