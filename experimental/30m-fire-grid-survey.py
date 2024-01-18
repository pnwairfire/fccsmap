#!/usr/bin/env python3

import argparse
import csv
import importlib
import json
import logging
import rasterio
import rasterio.features
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


  Area south of HI which ends up within the bounds of the tif file

    {script} -w -156.9 -e -156.8 -s 13.0 -n 13.1 \\
      -f ~/WFEIS-30m-FCCS-LANDFIRE-data/LF2022_FCCS_220_HI/Tif/LH22_FCCS_220.tif \\
      -j ./30m-fccs-SouthOfHawaii-output.json

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

def get_fccs_grid(args):
    # The tiff object has the following attrs
    #  bounds e.g.:  BoundingBox(left=-2362395.000000002, bottom=221265.00000000373, right=2327654.999999998, top=3267405.0000000037)
    #  crs, e.g.: CRS.from_epsg(5070)
    #  res, e.g.: (30.0, 30.0)
    #  shape, e.g.: (101538, 156335)

    # read the data and create the shapes
    with rasterio.open(args.geo_tiff_file) as tiff:
        data = tiff.read(1)
        data = data.astype('int16')

        grid_shapes = rasterio.features.shapes(
            data, mask=None, transform=tiff.transform)
        crs = tiff.crs
        res = tiff.res

    # read the shapes as separate lists
    fccs_ids = []
    geometry = []
    for shape, value in grid_shapes:
        # We'll use centroids of FCCS grid cells to speed up spatial joins, below
        geometry.append(shapely.geometry.shape(shape).centroid)
        fccs_ids.append(value)

    # build the gdf object over the two lists
    gdf = geopandas.GeoDataFrame({
            'fccs_id': fccs_ids,
            'geometry': geometry
        }, crs=crs)

    if  crs.to_string() != 'EPSG:5070':
        gdf = gdf.to_crs('EPSG:5070')

    import pdb;pdb.set_trace()
    return gdf


if __name__ == '__main__':
    args = parse_args()


    logging.basicConfig(format='%(asctime)s [%(levelname)s]:%(message)s',
        level=getattr(logging, args.log_level))

    logging.info("Getting fire grid")
    fire_grid = get_fire_grid(args)

    logging.info("Getting FCCS grid")
    fccs_grid = get_fccs_grid(args)

    logging.info("Running sjoin on GeoDataFrames")
    df = fire_grid.sjoin(fccs_grid)

    logging.info("Iterating through result of sjoin")
    fccs_ids_by_fire_grid_cell_idx = defaultdict(lambda: [])
    for fire_grid_index, series_obj in df.iterrows():
        # Notes:
        #  - fire_grid_index -- the index of the grid cell in the
        #    one dimensional fire_grid.geometry array
        #  - series_obj.geometry == fire_grid.geometry[fire_grid_index]
        #  - series_obj.lt_ln -- the y,x indices of the grid cell in the fire grid
        #  - series_obj.index_right -- the index of the point in the one
        #    dimensional fccs_grid.geometry array

        #key = ','.join([str(e) for e in series_obj.lt_ln])
        key = fire_grid_index
        fccs_ids_by_fire_grid_cell_idx[key].append(series_obj.fccs_id)

    fire_grid_4326 = fire_grid.to_crs('EPSG:4326')

    results = []
    for i, fire_grid_polygon in enumerate(fire_grid_4326.geometry):
        fccs_ids = fccs_ids_by_fire_grid_cell_idx[i]

        # get count by FCCS id
        # TODO: keep track of non-land, non-forested fuelbeds separately
        total_counts = defaultdict(lambda: 0)
        for fccs_id in fccs_ids:
            total_counts[fccs_id] += 1
        total = sum(total_counts.values())

        # compute fuelbed percentages
        fuelbeds =  {
            str(k): {
                'percent': 100.0 * float(v)/float(total), 'grid_cells': v
            } for k,v in list(total_counts.items())
        }

        # TODO: Keep only the most prevalent FCCS IDs that comprise 90% of the
        #    remaining cells.   Potentially: Truncate to 5 FCCS IDs max.
        #    Renormalize to the truncated total.

        # shapely.geometry.mapping produces a GeoJSON feature
        e = shapely.geometry.mapping(fire_grid_polygon)
        e['properties'] = {
            'fuelbeds': fuelbeds,
            'lat_lng_indiices': fire_grid.lt_ln[i],
        }
        results.append(e)

    if args.json_output_file:
        with open(args.json_output_file, 'w') as f:
            f.write(json.dumps(results))

    if args.csv_output_file:
        logging.warning("CSV output not yet implemented")
