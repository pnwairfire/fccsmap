#!/usr/bin/env python3

import argparse
import csv
import importlib
import json
import logging
import rasterio
import rasterio.features
import rioxarray
import shapely
import sys
from collections import defaultdict

try:
    pass # TODO: import any required fccsmap modules
except:
    import os
    root_dir = os.path.abspath(os.path.join(sys.path[0], '../'))
    sys.path.insert(0, root_dir)
    pass # TODO: import any required fccsmap modules


# TODO: if fire grid is large enough, break it up, work on pieces
#    individually, then join results


EXAMPLES_STRING = """
Examples:

  Lower 48

    {script} -w -130.0 -e -64.0 -s 19.0 -n 50.0 \\
      -f ~/WFEIS-30m-FCCS-LANDFIRE-data/LF2022_FCCS_220_CONUS/Tif/LC22_FCCS_220.tif \\
      -j ./30m-fccs-Lower48-output.json

  Area around Winthrop, WA

    {script} -w -120.3 -e -120.1 -s 48.4 -n 48.5 \\
      -f ~/WFEIS-30m-FCCS-LANDFIRE-data/LF2022_FCCS_220_CONUS/Tif/LC22_FCCS_220.tif \\
      -j ./30m-fccs-WinthropWA-output.json

  Hawaii:

    {script} -w -160.5 -e -154.5 -s 19.0 -n 22.4 \\
      -f ~/WFEIS-30m-FCCS-LANDFIRE-data/LF2022_FCCS_220_HI/Tif/LH22_FCCS_220.tif \\
      -j ./30m-fccs-Hawaii-output.json

  Area on west side of the Big Island (Hawaii)

    {script} -w -155.2 -e -155.1 -s 19.5 -n 19.6 \\
      -f ~/WFEIS-30m-FCCS-LANDFIRE-data/LF2022_FCCS_220_HI/Tif/LH22_FCCS_220.tif \\
      -j ./30m-fccs-HawaiiBigIsland-output.json

  Area on Maui

    {script} -w -156.3 -e -156.2 -s 20.7 -n 20.8 \\
      -f ~/WFEIS-30m-FCCS-LANDFIRE-data/LF2022_FCCS_220_HI/Tif/LH22_FCCS_220.tif \\
      -j ./30m-fccs-HawaiiMaui-output.json
 """.format(script=sys.argv[0])

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--fire-grid-bounds-west', required=True,
        type=float, help="Western boundary of fire grid")
    parser.add_argument('-e', '--fire-grid-bounds-east', required=True,
        type=float, help="Eastern boundary of fire grid")
    parser.add_argument('-s', '--fire-grid-bounds-south', required=True,
        type=float, help="Southern boundary of fire grid")
    parser.add_argument('-n', '--fire-grid-bounds-north', required=True,
        type=float, help="Northern boundary of fire grid")
    parser.add_argument('-r', '--fire-grid-resolution',
        type=float, default=3000, help="Resolution (in meters) of fire grid")
    parser.add_argument('-f', '--geo-tiff-file', required=True,
        help="full pathname to GeoTIFF file containing FCCS data")
    parser.add_argument('-j', '--json-output-file',
        help="full pathname of JSON output file to be generated")
    parser.add_argument('-c', '--csv-output-file',
        help="full pathname of CSV output file to be generated")
    parser.add_argument('--tiff-load-implementation', default='rasterio',
        help="options: 'rasterio', 'rioxarray'")

    parser.add_argument('--log-level', default='INFO', help="Log level")

    parser.epilog = EXAMPLES_STRING
    parser.formatter_class = argparse.RawTextHelpFormatter
    return parser.parse_args()


###############################################################################
# The following was copied from from FIS and modified slightly
#    pnwairfire-fire-information-systems/fire-grid/define_grid.py

from typing import *
import numpy
import geopandas
from shapely.geometry import Polygon

def define_grid_proj(bbox: List[float], res: float) -> geopandas.GeoDataFrame:
    # wgs84 polygon box (main)
    ll = (bbox[0], bbox[2])
    ul = (bbox[0], bbox[3])
    ur = (bbox[1], bbox[3])
    lr = (bbox[1], bbox[2])
    wgs84_box = geopandas.GeoDataFrame({'geometry': [Polygon([ll, ul, ur, lr])]}, crs="EPSG:4326")

    # to albers
    epsg5070_box = wgs84_box.to_crs('EPSG:5070')

    # Use
    proj_bbox = epsg5070_box.bounds
    proj_bbox = [proj_bbox['minx'].to_list()[0] // 1,
                 proj_bbox['maxx'].to_list()[0] // 1 + 1,
                 proj_bbox['miny'].to_list()[0] // 1,
                 proj_bbox['maxy'].to_list()[0] // 1 + 1]
    y_array = numpy.arange(proj_bbox[2], proj_bbox[3] + res, res)
    x_array = numpy.arange(proj_bbox[0], proj_bbox[1] + res, res)

    polygons = []
    lt_ln = []
    for lt in range(len(y_array)):
        for ln in range(len(x_array)):
            ll = (x_array[ln], y_array[lt])
            ul = (x_array[ln], y_array[lt] + res)
            ur = (x_array[ln] + res, y_array[lt] + res)
            lr = (x_array[ln] + res, y_array[lt])
            polygons.append(Polygon([ll, ul, ur, lr]))
            lt_ln.append([lt, ln])

    return geopandas.GeoDataFrame({
            'geometry': polygons,
            'lt_ln': lt_ln
        }, crs="EPSG:5070")


###############################################################################

def get_fire_grid(args):
    bounds = [
        args.fire_grid_bounds_west,
        args.fire_grid_bounds_east,
        args.fire_grid_bounds_south,
        args.fire_grid_bounds_north,
    ]
    grid = define_grid_proj(bounds, args.fire_grid_resolution)

    return grid

def get_fccs_grid_rioxarray(args, fire_grid):
    # See https://gis.stackexchange.com/questions/365538/exporting-geotiff-raster-to-geopandas-dataframe
    logging.info("Reading FCCS grid tif file with rioxarray")
    raster = rioxarray.open_rasterio(infile)

    import pdb;pdb.set_trace()

    raise NotImplementedError("Haven't yet implemented loading tiff data into GeoDataFrame with rioxarray")

def get_fccs_grid_rasterio(args, fire_grid):
    # The tiff object has the following attrs
    #  bounds e.g.:  BoundingBox(left=-2362395.000000002, bottom=221265.00000000373, right=2327654.999999998, top=3267405.0000000037)
    #  crs, e.g.: CRS.from_epsg(5070)
    #  res, e.g.: (30.0, 30.0)
    #  shape, e.g.: (101538, 156335)

    # read the data and create the shapes
    logging.info("Reading FCCS grid tif file with rasterio")
    with rasterio.open(args.geo_tiff_file) as tiff:
        data = tiff.read(1)
        data = data.astype('int16')
        crs = tiff.crs
        res = tiff.res

        # TODO: Can we crop `data` here to exclude anything outside of the
        #   fire grid (based on `fire_grid.to_crs(crs).total_bounds`)?
        #   If we can, remove use of `fire_grid_bounds`, below

        # TODO: read docs on `mask` kwarg
        # TODO: use other method or package, since docs say that
        #   that it uses large amounts of memory when there's high
        #   pixel-to-variability
        #   https://rasterio.readthedocs.io/en/latest/api/rasterio.features.html
        grid_shapes = rasterio.features.shapes(
            data, mask=None, transform=tiff.transform)

    # We'll use the fire grid total bounds to determine whether or not
    # to include fccs grid cells in the fccs grid dataframe, below
    fire_grid_bounds = fire_grid.to_crs(crs).total_bounds

    logging.info("Collecting lists of grid cell centers and FCCS Ids")
    # read the shapes as separate lists
    fccs_ids = []
    geometry = []
    omitted = 0
    for shape, value in grid_shapes:
        # We'll use centroids of FCCS grid cells to speed up spatial joins, below
        centroid = shapely.geometry.shape(shape).centroid
        if (centroid.x >= fire_grid_bounds[0] and centroid.x <= fire_grid_bounds[2]
                and centroid.y >= fire_grid_bounds[1] and centroid.x <= fire_grid_bounds[3]):
            geometry.append(centroid)
            fccs_ids.append(value)
        else:
            omitted += 1

    logging.info(f"Kept {len(geometry)} FCCS grid cells and omitted {omitted}")

    # build the gdf object over the two lists
    logging.info("Building FCCS GeoDataFrame")
    gdf = geopandas.GeoDataFrame({
            'fccs_id': fccs_ids,
            'geometry': geometry
        }, crs=crs)

    if  crs.to_string() != 'EPSG:5070':
        logging.info(f"Transforming FCCS GeoDataFrame from {crs.to_string()} to EPSG:5070")
        gdf = gdf.to_crs('EPSG:5070')

    return gdf


TRUNCATION_PCT_THRESHOLD = 90
TRUNCATION_NUM_THRESHOLD = None

def get_all_fuelbeds_per_grid_cell(fire_grid, fccs_grid):
    df = fccs_grid.sjoin(fire_grid, rsuffix='fire_grid')
    fpg = df.groupby(['fccs_id','index_fire_grid']).size().to_frame('count').reset_index()

    counts = defaultdict(lambda: {'counts': {}, 'total': 0})
    for _, obj in fpg.iterrows():
        idx = int(obj.index_fire_grid)
        fccs_id = str(int(obj.fccs_id))
        count = obj.count()
        counts[idx]['counts'][fccs_id] = count
        counts[idx]['total'] += count

    all_fuelbeds = {}
    for idx in counts:
        cell = counts[idx]
        all_fuelbeds[idx] = {
            k: {
                'pct': 100.0 * cell['counts'][k] / cell['total'],
                # If we don't cast `count` to int, we get an error when dumping to JSON:
                #   *** TypeError: Object of type int64 is not JSON serializable
                'count': int(cell['counts'][k])
            } for k in cell['counts']
        }

    return all_fuelbeds

def do_exclude(fccs_id):
    # TODO: implemented
    return False

def prune(all_fuelbeds):
    # Keep only the most prevalent FCCS IDs that comprise 90% of the
    #    remaining cells.   Potentially: Truncate to 5 FCCS IDs max.
    #    Renormalize to the truncated total.
    included = defaultdict(lambda: [])
    truncated = defaultdict(lambda: [])
    excluded = defaultdict(lambda: [])
    for idx in all_fuelbeds:
        total_pct = 0
        total_num = 0
        for fccs_id, d in sorted(all_fuelbeds[idx].items(), key=lambda e: -e[1]['pct']):
            fb = {'fccsId': fccs_id, **all_fuelbeds[idx][fccs_id]}
            if do_exclude(fccs_id):
                excluded[idx].append(fb)
            elif (total_pct >= TRUNCATION_PCT_THRESHOLD
                    or (TRUNCATION_NUM_THRESHOLD and total_num >= TRUNCATION_NUM_THRESHOLD)):
                truncated[idx].append(fb)
            else:
                included[idx].append(fb)

            total_pct += fb['pct']
            total_num += 1

    return included, truncated, excluded

if __name__ == '__main__':
    args = parse_args()

    logging.basicConfig(format='%(asctime)s [%(levelname)s]:%(message)s',
        level=getattr(logging, args.log_level))

    logging.info("Getting fire grid")
    fire_grid = get_fire_grid(args)

    logging.info("Getting FCCS grid")
    f = globals().get(f"get_fccs_grid_{args.tiff_load_implementation}")
    if not f:
        raise RuntimeError("Invalid tiff file load implementation - "
            f"{args.tiff_load_implementation}")
    fccs_grid = f(args, fire_grid)

    all_fuelbeds = get_all_fuelbeds_per_grid_cell(fire_grid, fccs_grid)
    included, truncated, excluded = prune(all_fuelbeds)

    results = []
    fire_grid_4326 = fire_grid.to_crs('EPSG:4326')
    for i, fire_grid_polygon in enumerate(fire_grid_4326.geometry):

        e = {
            "type": "Feature",
            # shapely.geometry.mapping produces a GeoJSON feature geometry
            "geometry": shapely.geometry.mapping(fire_grid_polygon),
            "properties": {
                'fuelbeds': included[i],
                'excluded': excluded[i],
                'truncated': truncated[i],
                'latLngIndiices': fire_grid.lt_ln[i],
            },
            "id": i
        }

        results.append(e)

    if args.json_output_file:
        with open(args.json_output_file, 'w') as f:
            f.write(json.dumps(results))

    if args.csv_output_file:
        logging.warning("CSV output not yet implemented")