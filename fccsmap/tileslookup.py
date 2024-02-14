"""fccsmap.tileslookup
"""

__author__      = "Joel Dubowy"

import os

import geopandas
import numpy
import rioxarray
import shapely

from . import BaseLookUp

__all__ = [
    'FccsTilesLookUp'
]

class FccsTilesLookUp(BaseLookUp):

    # OPTIONS_DOC_STRING used by Constructor docstring as well as
    # script helpstring
    OPTIONS_STRING = """
         - is_alaska -- Whether or not location is in Alaska; boolean
         - is_canada -- Whether or not location is in Canada; boolean
         - is_hawaii -- Whether or not location is in Hawaii; boolean
         - tiles_directory --
         - index_shapefile -- default: index.shp
         [- projection info file???]
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

    def _create_tiles_spatial_index(self, options):
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
        self._crs = self._tiles_df.crs


    ##
    ## Look-up helpers
    ##

    def _look_up(self, geo_data):
        geo_data_df = self._get_geo_data_df(geo_data)
        tiles = self._get_matching_tiles(geo_data_df)
        per_tile_stats = [self._look_up_tile(geo_data_df, tile) for tile in tiles]
        #stats = self._aggregate(per_tile_stats)
        final_stats = self._compute_percentages(per_tile_stats)
        return final_stats

    def _get_geo_data_df(self, geo_data):
        shape = shapely.geometry.shape(geo_data)
        wgs84_df = geopandas.GeoDataFrame({'geometry': [shape]}, crs="EPSG:4326")
        return wgs84_df.to_crs(self._crs)

    def _get_matching_tiles(self, geo_data_df):
        matches = self._tiles_df.sjoin(geo_data_df, rsuffix='geo_data')
        tiles = list(matches['location'])
        return tiles

    def _look_up_tile(self, geo_data_df, tile):
        tile_file = os.path.join(self._tiles_directory, tile)
        raster = rioxarray.open_rasterio(tile_file)
        band = raster[0]
        x, y, fccs_id = band.x.values, band.y.values, band.values
        # TODO: what do the following to steps do?
        x, y = numpy.meshgrid(x, y)
        x, y, fccs_id = x.flatten(), y.flatten(), fccs_id.flatten()
        fccs_df = geopandas.GeoDataFrame({
            'geometry': geopandas.GeoSeries.from_xy(x, y, crs=band.rio.crs),
            'fccs_id': fccs_id,
        })

        grid_cells = fccs_df.sjoin(geo_data_df, rsuffix='geo_data')
        fpg = grid_cells.groupby(['fccs_id']).size().to_frame('count').reset_index()
        stats = {'counts': {}, 'total': 0}
        for _, obj in fpg.iterrows():
            fccs_id = str(int(obj.get('fccs_id')))
            count = int(obj.get('count'))
            stats['counts'][fccs_id] = count
            stats['total'] += count

        return stats
