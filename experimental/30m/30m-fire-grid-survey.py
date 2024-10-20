#!/usr/bin/env python3

import argparse
import csv
import importlib
import json
import logging
import os
import sys
import typing
from collections import defaultdict
from functools import reduce

import geopandas
import numpy
import rasterio
import rasterio.features
import rioxarray
import shapely
from osgeo import gdal

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
      -f ~/30m-FCCS/LF2022_FCCS_220_CONUS/Tif/LC22_FCCS_220.tif \\
      -j {output_dirname}/30m-fccs-Lower48-output.json


  PNW 1.33km met bounds

    {script} -w -126.0 -e -111.0 -s 41.75 -n 49.25 \\
      -f ~/30m-FCCS/LF2022_FCCS_220_CONUS/Tif/LC22_FCCS_220.tif \\
      -j {output_dirname}/30m-fccs-PNW-1.33km-output.json

  Area around Winthrop, WA

    {script} -w -120.3 -e -120.1 -s 48.4 -n 48.5 \\
      -f ~/30m-FCCS/LF2022_FCCS_220_CONUS/Tif/LC22_FCCS_220.tif \\
      -j {output_dirname}/30m-fccs-WinthropWA-output.json

  Hawaii:

    {script} -w -160.5 -e -154.5 -s 19.0 -n 22.4 \\
      -f ~/30m-FCCS/LF2022_FCCS_220_HI/Tif/LH22_FCCS_220.tif \\
      -j {output_dirname}/30m-fccs-Hawaii-output.json

  Area on west side of the Big Island (Hawaii)

    {script} -w -155.2 -e -155.1 -s 19.5 -n 19.6 \\
      -f ~/30m-FCCS/LF2022_FCCS_220_HI/Tif/LH22_FCCS_220.tif \\
      -j {output_dirname}/30m-fccs-HawaiiBigIsland-output.json

  Area on Maui

    {script} -w -156.3 -e -156.2 -s 20.7 -n 20.8 \\
      -f ~/30m-FCCS/LF2022_FCCS_220_HI/Tif/LH22_FCCS_220.tif \\
      -j {output_dirname}/30m-fccs-HawaiiMaui-output.json
 """.format(script=sys.argv[0],
        output_dirname=os.path.join(os.path.dirname(sys.argv[0]), 'output'))

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
    parser.add_argument('--shapefile-output',
        help="full pathname of shapefile to be generated")

    parser.add_argument('--log-level', default='INFO', help="Log level")

    parser.epilog = EXAMPLES_STRING
    parser.formatter_class = argparse.RawTextHelpFormatter
    return parser.parse_args()

##
## Fire Grid
##

def define_grid_proj(bbox: typing.List[float], res: float) -> geopandas.GeoDataFrame:
    """The following was copied from from FIS and modified slightly
    pnwairfire-fire-information-systems/fire-grid/define_grid.py
    """
    # wgs84 polygon box (main)
    ll = (bbox[0], bbox[2])
    ul = (bbox[0], bbox[3])
    ur = (bbox[1], bbox[3])
    lr = (bbox[1], bbox[2])
    wgs84_box = geopandas.GeoDataFrame({'geometry': [shapely.Polygon([ll, ul, ur, lr])]}, crs="EPSG:4326")

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
            polygons.append(shapely.Polygon([ll, ul, ur, lr]))
            lt_ln.append([lt, ln])

    return geopandas.GeoDataFrame({
            'geometry': polygons,
            'lt_ln': lt_ln
        }, crs="EPSG:5070")


def get_fire_grid(args):
    bounds = [
        args.fire_grid_bounds_west,
        args.fire_grid_bounds_east,
        args.fire_grid_bounds_south,
        args.fire_grid_bounds_north,
    ]
    grid = define_grid_proj(bounds, args.fire_grid_resolution)

    return grid

##
## FCCS Grid
##

def crop_tiff_file(tiff_file, fire_grid):

    with rasterio.open(args.geo_tiff_file) as tiff:
        # total_bounds returns an array like:
        #   array([ 64781.47742873, 847703.76037809,  93523.38640148, 877718.77342049])
        # which is
        #   [left, bottom, right, top]
        fg_bounds = fire_grid.to_crs(tiff.crs).total_bounds

        # window need to be (left, top, right, bottom)
        window = (fg_bounds[0], fg_bounds[3], fg_bounds[2], fg_bounds[1])

        cropped_tiff_file = '/tmp/' + os.path.basename(args.geo_tiff_file).replace('.tif', '-cropped.tif')

        #gdal.Translate(cropped_tiff_file, tiff, projWin=tuple(window))
        gdal.Translate(cropped_tiff_file, args.geo_tiff_file, projWin=window)

        return cropped_tiff_file

def get_fccs_grid(cropped_tiff_file):
    # Note: the following produced the same gdf, but too > 20x as long
    #  See https://gis.stackexchange.com/questions/394455/how-to-find-coordinates-of-pixels-of-a-geotiff-image-with-python
    #     rds = rioxarray.open_rasterio(cropped_tiff_file)
    #     crs = rds[0].rio.crs.to_string()
    #     rds = rds.squeeze().drop("spatial_ref").drop("band")
    #     rds.name = "fccs_id"
    #     df = rds.to_dataframe().reset_index()
    #     geometry = [shapely.Point(xy) for xy in zip(df.x, df.y)]
    #     df = df.drop(['x', 'y'], axis=1)
    #     gdf = geopandas.GeoDataFrame(df, crs=crs, geometry=geometry)

    # See https://gis.stackexchange.com/questions/365538/exporting-geotiff-raster-to-geopandas-dataframe
    logging.info("Reading FCCS grid tif file with rioxarray")
    raster = rioxarray.open_rasterio(cropped_tiff_file)

    # get first band of raster
    band = raster[0]
    x, y, fccs_id = band.x.values, band.y.values, band.values
    # TODO: what do the following to steps do?
    x, y = numpy.meshgrid(x, y)
    x, y, fccs_id = x.flatten(), y.flatten(), fccs_id.flatten()

    # create new geoseries with centroid geometries
    gdf = geopandas.GeoDataFrame({
        'geometry': geopandas.GeoSeries.from_xy(x, y, crs=band.rio.crs),
        'fccs_id': fccs_id,
    })

    if band.rio.crs.to_string() != 'EPSG:5070':
        logging.info(f"Transforming FCCS GeoDataFrame from {band.rio.crs.to_string()} to EPSG:5070")
        gdf = gdf.to_crs('EPSG:5070')

    return gdf


##
## Process fuelbeds
##

TRUNCATION_PCT_THRESHOLD = 90
TRUNCATION_NUM_THRESHOLD = None

def get_all_fuelbeds_per_grid_cell(fire_grid, fccs_grid):
    df = fccs_grid.sjoin(fire_grid, rsuffix='fire_grid')
    fpg = df.groupby(['fccs_id','index_fire_grid']).size().to_frame('count').reset_index()

    counts = defaultdict(lambda: {'counts': {}, 'total': 0})
    for _, obj in fpg.iterrows():
        idx = int(obj.get('index_fire_grid'))
        fccs_id = str(int(obj.get('fccs_id')))
        count = int(obj.get('count'))
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
    fccs_id = int(fccs_id)
    if fccs_id < 1:
        # 0 (bare ground) or negative values (which mean what?)
        return True

    # TODO: other cases?
    return False

def split_by_burnability(all_fuelbeds):
    burnable = defaultdict(lambda: [])
    unburnable = defaultdict(lambda: [])
    for idx in all_fuelbeds:
        for fccs_id, d in sorted(all_fuelbeds[idx].items(), key=lambda e: -e[1]['pct']):
            fb = {'fccsId': fccs_id, **all_fuelbeds[idx][fccs_id]}
            if do_exclude(fccs_id):
                unburnable[idx].append(fb)
            else:
                burnable[idx].append(fb)

        # compute % of burnable
        total_burnable_pct = reduce(lambda a,b: a + b['pct'], burnable[idx], 0)
        p_factor = 100 / total_burnable_pct
        for fb in burnable[idx]:
            fb['bpct'] = p_factor * fb['pct']

    return burnable, unburnable

def truncate(burnable):
    included = defaultdict(lambda: [])
    truncated = defaultdict(lambda: [])
    for idx in burnable:
        total_pct = 0
        total_num = 0
        for fb in sorted(burnable[idx], key=lambda e: -e['bpct']):
            if (total_pct >= TRUNCATION_PCT_THRESHOLD
                    or (TRUNCATION_NUM_THRESHOLD and total_num >= TRUNCATION_NUM_THRESHOLD)):
                truncated[idx].append(fb)
            else:
                included[idx].append(fb)

            total_pct += fb['bpct']
            total_num += 1

    return included, truncated

def calculate_pct_in_group(fuelbeds, total_burnable_pct=None):
    if not fuelbeds:
        return

    total = reduce(lambda a,b: a + b['pct'], fuelbeds, 0)
    p_factor = 100 / total
    for fb in fuelbeds:
        fb['npct'] = p_factor * fb['pct']

def prune(all_fuelbeds):
    logging.info("Pruning fuelbeds")
    # First, separate out unburnable
    burnable, unburnable = split_by_burnability(all_fuelbeds)
    included, truncated = truncate(burnable)

    logging.info("Recalculating %'s")
    for i in all_fuelbeds:
        calculate_pct_in_group(included[i])
        calculate_pct_in_group(truncated[i])
        calculate_pct_in_group(unburnable[i])

    logging.info("Done pruning fuelbeds and recalculating %'s")
    return included, truncated, unburnable

OUTPUT_CRS = 'EPSG:4326'

if __name__ == '__main__':
    args = parse_args()

    logging.basicConfig(format='%(asctime)s [%(levelname)s]:%(message)s',
        level=getattr(logging, args.log_level))

    logging.info("Computing fire grid")
    fire_grid = get_fire_grid(args)

    logging.info("Cropping tiff file")
    cropped_tiff_file = crop_tiff_file(args.geo_tiff_file, fire_grid)

    logging.info("Loading FCCS grid")
    fccs_grid = get_fccs_grid(cropped_tiff_file)

    logging.info("Determining fuelbeds per grid cell")
    all_fuelbeds = get_all_fuelbeds_per_grid_cell(fire_grid, fccs_grid)
    included, truncated, unburnable = prune(all_fuelbeds)

    logging.info("Forming output")
    results = []
    output_fire_grid = fire_grid.to_crs(OUTPUT_CRS)
    for i, fire_grid_polygon in enumerate(output_fire_grid.geometry):

        e = {
            "type": "Feature",
            # shapely.geometry.mapping produces a GeoJSON feature geometry
            "geometry": shapely.geometry.mapping(fire_grid_polygon),
            "properties": {
                'crs': OUTPUT_CRS,
                'included': included[i],
                'truncated': truncated[i],
                'unburnable': unburnable[i],
                'latLngIndiices': fire_grid.lt_ln[i],
            },
            "id": i
        }

        results.append(e)

    if args.json_output_file:
        logging.info("Writing json output")
        with open(args.json_output_file, 'w') as f:
            f.write(json.dumps(results))
        # The following produces a huge file, compared to the main output file
        # with open(args.json_output_file.replace('.json', '-fccs-grid.json'), 'w') as f:
        #     f.write(fccs_grid.to_json())

    if args.csv_output_file:
        logging.warning("CSV output not yet implemented")

    if args.shapefile_output:
        # TODO: create GeoDataFrame from results and then call
        # df.to_file(args.shapefile_output, crs=df.crs)
        logging.warning("--shapefile not yet implemented")
