#!/usr/bin/env python3

import argparse
import importlib
import rasterio
import sys

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
      -f ~/WFEIS-30m-FCCS-LANDFIRE-data/LF2022_FCCS_220_CONUS/Tif/LC22_FCCS_220.tif

  Area around Winthrop, WA

    {script} -w -120.3 -e -120.1 -s 48.4 -n 48.5 \\
      -f ~/WFEIS-30m-FCCS-LANDFIRE-data/LF2022_FCCS_220_CONUS/Tif/LC22_FCCS_220.tif

  Hawaii:

    {script} -w -160.5 -e -154.5 -s 19.0 -n 22.4 \\
      -f ~/WFEIS-30m-FCCS-LANDFIRE-data/LF2022_FCCS_220_HI/Tif/LH22_FCCS_220.tif

  Area on west side of the Big Island (Hawaii)

    {script} -w -155.2 -e -155.1 -s 19.5 -n 19.6 \\
      -f ~/WFEIS-30m-FCCS-LANDFIRE-data/LF2022_FCCS_220_HI/Tif/LH22_FCCS_220.tif

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
    parser.add_argument('-f', '--geo-tiff-file', required=True,
        help="full pathname to GeoTIFF file containing FCCS data")

    parser.epilog = EXAMPLES_STRING
    parser.formatter_class = argparse.RawTextHelpFormatter
    return parser.parse_args()


###############################################################################
# The following was copied from from FIS and modified slightly
#    pnwairfire-fire-information-systems/fire-grid/define_grid.py

from typing import *
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon

def define_grid_proj(bbox: List[float], bbox_ak: List[float] = None) -> gpd.GeoDataFrame:
    """
    1.5 km = 1500 m
    3 km = 3000 m
    """
    def _create_poly_grid_list(bbox):
        # wgs84 polygon box (main)
        ll = (bbox[0], bbox[2])
        ul = (bbox[0], bbox[3])
        ur = (bbox[1], bbox[3])
        lr = (bbox[1], bbox[2])
        wgs84_box = gpd.GeoDataFrame({'geometry': [Polygon([ll, ul, ur, lr])]}, crs="EPSG:4326")
        # to albers
        epsg5070_box = wgs84_box.to_crs('EPSG:5070')
        proj_bbox = epsg5070_box.bounds
        proj_bbox = [proj_bbox['minx'].to_list()[0] // 1,
                     proj_bbox['maxx'].to_list()[0] // 1 + 1,
                     proj_bbox['miny'].to_list()[0] // 1,
                     proj_bbox['maxy'].to_list()[0] // 1 + 1]
        res = 3000
        y_array = np.arange(proj_bbox[2], proj_bbox[3] + res, res)
        x_array = np.arange(proj_bbox[0], proj_bbox[1] + res, res)
        polygons = []
        for lt in range(len(y_array)):
            for ln in range(len(x_array)):
                ll = (x_array[ln], y_array[lt])
                ul = (x_array[ln], y_array[lt] + res)
                ur = (x_array[ln] + res, y_array[lt] + res)
                lr = (x_array[ln] + res, y_array[lt])
                polygons.append(Polygon([ll, ul, ur, lr]))
        return polygons
    polys_conus = _create_poly_grid_list(bbox=bbox)
    if bbox_ak:
        polys_ak = _create_poly_grid_list(bbox=bbox_ak)
        polys_conus.extend(polys_ak)
    model_grid_gpd = gpd.GeoDataFrame({'geometry': polys_conus}, crs="EPSG:5070")
    return model_grid_gpd

###############################################################################

def get_fire_grid(args):
    bounds = [
        args.fire_grid_bounds_west,
        args.fire_grid_bounds_east,
        args.fire_grid_bounds_south,
        args.fire_grid_bounds_north,
    ]
    grid = define_grid_proj(bbox=bounds) #, bbox_ak=[-172.0, -125.0, 53.0, 72.0])

    # TODO: do stuff?

    return grid

def get_tiff_grid(tiff):
    # The tiff object has the following attrs
    #  bounds e.g.:  BoundingBox(left=-2362395.000000002, bottom=221265.00000000373, right=2327654.999999998, top=3267405.0000000037)
    #  crs, e.g.: CRS.from_epsg(5070)
    #  res, e.g.: (30.0, 30.0)
    #  shape, e.g.: (101538, 156335)

    # TODO: do stuff

    return tiff

if __name__ == '__main__':
    args = parse_args()

    fire_grid = get_fire_grid(args)
    tiff = rasterio.open(args.geo_tiff_file)
    tiff_grid = get_tiff_grid(tiff)
