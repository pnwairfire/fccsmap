"""fccsmap.tileslookup
"""

__author__      = "Joel Dubowy"

import logging
import os
from collections import defaultdict

import geopandas
import numpy
import rioxarray
import shapely

from . import BaseLookUp, time_me

__all__ = [
    'FccsTilesLookUp'
]

class FccsTilesLookUp(BaseLookUp):

    # OPTIONS_DOC_STRING used by Constructor docstring as well as
    # script helpstring
    OPTIONS_STRING = """
         - tiles_directory -- directory containing tiles
         - index_shapefile -- default: index.shp
    """

    def __init__(self, **options):
        """Constructor

        Valid options:

        {}

        """.format(self.OPTIONS_STRING + self.ADDITIONAL_OPTIONS_STRING)

        self._set_tiles_directory(options)
        self._create_tiles_spatial_index(options)

        super().__init__(**options)

    ##
    ## Constructor methods
    ##

    def _set_tiles_directory(self, options):
        if not options.get('tiles_directory'):
            raise RuntimeError("Missing required config option 'tiles_directory'")

        self._tiles_directory = os.path.abspath(options['tiles_directory'])
        if not os.path.exists(self._tiles_directory):
            raise RuntimeError(f"Tiles directory does not exist - {self._tiles_directory}")

    @time_me()
    def _create_tiles_spatial_index(self, options):
        logging.debug("Creating tiles index")

        # if not specified, assume index shapefile is named index.shp and
        # exists in the files directory
        index_shapefile = options.get('index_shapefile') or os.path.join(self._tiles_directory, "index.shp")

        # If index_shapefile has no path (is only a file name) and if the file
        # does not exist in the current dir, then assume it's in the tiles directory
        if (os.path.basename(index_shapefile) == index_shapefile
                and not os.path.exists(os.path.abspath(index_shapefile))):
            index_shapefile = os.path.join(self._tiles_directory, index_shapefile)

        index_shapefile = os.path.abspath(index_shapefile)

        if not os.path.exists(index_shapefile):
            raise RuntimeError(f"Tiles index shapefile does not exist - {index_shapefile}")

        self._tiles_df = geopandas.read_file(index_shapefile)
        #self._tiles_index = self._tiles_df.sindex

        # TODO: set `self._sampling_radius_km` to grid resolution

        self._crs = self._tiles_df.crs

    ##
    ## Look-up helpers
    ##

    @time_me()
    def _look_up(self, geo_data):
        geo_data_df = self._create_geo_data_df(geo_data)
        tiles = self._find_matching_tiles(geo_data_df)

        per_tile_stats = [
            self._look_up_in_file(
                geo_data_df,
                os.path.join(self._tiles_directory, tile)
            )
            for tile in tiles
        ]

        return self._aggregate(per_tile_stats, geo_data_df)

    @time_me()
    def _find_matching_tiles(self, geo_data_df):
        logging.debug("Finding matching tiles")
        matches = self._tiles_df.sjoin(geo_data_df, rsuffix='geo_data')
        tiles = list(matches['location'])
        return tiles

    @time_me()
    def _aggregate(self, per_tile_stats, geo_data_df):
        grid_cells = sum([s['grid_cells'] for s in per_tile_stats])
        fuelbeds = defaultdict(lambda: {'grid_cells': 0})
        for stats in per_tile_stats:
            for fccs_id, fb in stats['fuelbeds'].items():
                fuelbeds[fccs_id]['grid_cells'] += fb['grid_cells']

        for fb in fuelbeds.values():
            fb['percent'] = (fb['grid_cells'] / grid_cells) * 100.0

        return {
            'fuelbeds': fuelbeds,
            'grid_cells': grid_cells,
            'area': geo_data_df.area[0],
            'units': 'm^2'
        }
