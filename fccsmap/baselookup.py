import abc
import datetime
import json
import logging
import math
from collections import defaultdict, OrderedDict

import geopandas
import numpy
from rasterstats import zonal_stats
import rioxarray
import shapely

__all__ = [
    "time_me", "BaseLookUp"
]

def time_me(message_header="TIME-ME"):
    def _time_me(func):
        def _(*args, **kwargs):
            n = datetime.datetime.now()
            r = func(*args,  **kwargs)
            t = (datetime.datetime.now() - n).total_seconds()
            logging.debug(f"{message_header}: {func.__name__} {t}s")
            return r
        return _
    return _time_me


class BaseLookUp(metaclass=abc.ABCMeta):

    CONFIG_DEFAULTS = {
        "ignored_fuelbeds": ('0', '900'),
        "ignored_percent_resampling_threshold": 99.9,  # instead of 100.0, to account for rounding errors
        "insignificance_threshold": 10.0, # set to 0 to not remove
        "max_fuelbed_count_threshold": None,
        "no_sampling": False,
        "sampling_radius_km": 1.0,
        "sampling_radius_factors": [1, 3, 5],
        "use_all_grid_cells": False,
    }

    OPTIONS_STRING = """
         - ignored_fuelbeds -- fuelbeds to ignore
         - ignored_percent_resampling_threshold -- percentage of ignored
            fuelbeds which should trigger resampling in larger area; only
            plays a part in Point and MultiPoint look-ups
         - insignificance_threshold -- remove least prevalent fuelbeds that
            cumulatively add up to no more that this percentage; default: 10.0
         - max_fuelbed_count_threshold -- maximum number of fuelbeds to return
         - no_sampling -- don't sample surrounding area for Point
            and MultiPoint geometries
         - sampling_radius_km -- distance, in km, from points to start sampling
         - sampling_radius_factors -- increasing size of sampling area,
            expressed as a factor times the sampling radius (or grid resolution,
            for the bundled netcdf data).
            e.g. With 1km data, [1,3,5] would mean sampling a 2km x 2km area around
            the point, followed by a 6km x 6km area, and finally a 10km x 10km
            area (if necessary).
         - use_all_grid_cells -- Consider FCCS map grid cells entirely within
            the area of interest as well as cells partially outside of the area.
            (The default behavior is to ignore partial cells, unless there are no
            fully included cells, in which case parials are used.)
    """

    ADDITIONAL_OPTIONS_STRING = ""  # optionally defined in derived classes



    def __init__(self, **options):
        """Constructor

        Valid options:

        {}
        """.format(self.OPTIONS_STRING)

        for k in self.CONFIG_DEFAULTS:
            attr = f"_{k}"
            if not hasattr(self, attr):
                val = options[k] if options.get(k) is not None else self.CONFIG_DEFAULTS[k]
                logging.debug(f"Setting {attr} to {val}")
                setattr(self, attr, val)

    ##
    ## Public Interface
    ##

    def look_up(self, geo_data, area_acres=None):
        """Looks up FCCS fuelbed information within a region defined by
        multipolygon region

        Arguments
         - geo_data -- vector data, json formatted (or already loaded)

        Kwargs
        - area_acres -- only relevent to Point and MultiPoint data

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

        if not self._no_sampling and geo_data["type"] in ('Point', 'MultiPoint'):

            # If area_acres is defined, and if this is a MultiPoint, we want
            # to search an area around each point based on its fraction of
            # the total area. So, divide area_acres by the number of points
            area_acres_per_point = (
                (area_acres / len(geo_data['coordinates']))
                if (area_acres and geo_data["type"] == 'MultiPoint')
                else area_acres
            )

            sampling_radius_km = self._sampling_radius_from_area(area_acres_per_point)

            for radius_factor in self._sampling_radius_factors:
                logging.debug(f"Sampling {radius_factor} * sampling radius")

                new_geo_data = self._transform_points(geo_data,
                    radius_factor * sampling_radius_km)
                stats = self._look_up(new_geo_data)
                logging.debug(f"Stats from sampling {stats}")

                if not self._has_high_percent_of_ignored(stats):
                    break
            # at this point, if all water, we'll stick with it

            stats['sampled_grid_cells'] = stats.pop('grid_cells', None)
            stats['sampled_area'] = stats.pop('area', None)

        else:
            stats = self._look_up(geo_data)

        stats = self._remove_ignored(stats)
        stats = self._truncate(stats)

        # Sort fuelbeds by pct, decreasing
        stats['fuelbeds'] = OrderedDict({
            k: fb for k,fb
                in reversed(sorted(list(stats['fuelbeds'].items()),
                    key=lambda e: e[1]['percent']))
        })


        return stats

    ##
    ## Helper methods
    ##

    SQUARE_KM_PER_ACRE = 0.00404686

    def _sampling_radius_from_area(self, area_acres):
        if not area_acres:
            return self._sampling_radius_km

        area_square_km = area_acres * self.SQUARE_KM_PER_ACRE
        dim = math.sqrt(area_square_km)
        return dim / 2


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

    @abc.abstractmethod
    def _look_up(self, geo_data):
        """Returns data structured as follows:

            {
                'area': 36131660.998113036,
                'fuelbeds': {
                    '22': {'grid_cells': 1, 'percent': 2.7027027027027026},
                    '24': {'grid_cells': 1, 'percent': 2.7027027027027026},
                    '52': {'grid_cells': 34, 'percent': 91.89189189189189},
                    '59': {'grid_cells': 1, 'percent': 2.7027027027027026}},
                'grid_cells': 37,
                'units': 'm^2'
            }

        """
        pass

    @time_me()
    def _create_geo_data_df(self, geo_data):
        logging.debug("Creating data frame of geo-data")
        shape = shapely.geometry.shape(geo_data)
        wgs84_df = geopandas.GeoDataFrame({'geometry': [shape]}, crs="EPSG:4326")
        return wgs84_df.to_crs(self._crs)

    @time_me()
    def _look_up_in_file(self, geo_data_df, filename):
        """Determines the fuelbeds represented within geo_data_df and computes
        the percentage of each.  It does this by finding the grid cells whose
        centers are within geo_data_df and counts each with equal weight.
        """
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

        stats = zonal_stats(geo_data_df, filename,
            add_stats={'counts':counts})
        # TODO: make sure area units are correct and properly translated
        # to real geographical area; read them from nc file
        # TODO: read and include grid cell size from nc file
        final_stats = self._compute_percentages(stats)
        final_stats.update(area=geo_data_df.area[0], units='m^2')
        return final_stats

    def _has_high_percent_of_ignored(self, stats):
        return (self._compute_total_percent_ignored(stats) >=
            self._ignored_percent_resampling_threshold)

    def _compute_total_percent_ignored(self, stats):
        return sum([
            stats.get('fuelbeds', {}).get(fccs_id, {}).get('percent') or 0
                for fccs_id in self._ignored_fuelbeds
        ])

    def _compute_percentages(self, stats):
        """Inputs and array of stats like the following:
            [
                {
                    'count': 200,
                    'counts': {
                        0: 100,
                        72: 60,
                        346: 40
                    },
                    'max': 346.0, /* not used */
                    'mean': 106.0, /* not used */
                    'min': 0.0 /* not used */
                },
                {
                    'count': 100,
                    'counts': {
                        0: 70,
                        52: 30
                    },
                    'max': 52.0, /* not used */
                    'mean': 26, /* not used */
                    'min': 0.0 /* not used */
                }
            ]

        and poduces

            {

                'fuelbeds': {
                    '0': {'grid_cells': 170, 'percent': 56.6666667},
                    '72': {'grid_cells': 60, 'percent': 20.0},
                    '346': {'grid_cells': 40, 'percent': 13.333333},
                    '52': {'grid_cells': 30, 'percent': 10.0},
                },
                'grid_cells': 300
            }

        """
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

    def _truncate(self, stats):
        """Removes fuelbeds that make up an insignificant fraction of the
        total fuelbed composition (i.e. those that cumulatively make up
        less than insignificance_threshold), then remove the least prevalent
        of the remaining fuelbeds that are over the max_fuelbed_count_threshold,
        and then readjusts percentages so that they add up to 100.
        """
        if ((not self._insignificance_threshold
                    or self._insignificance_threshold <= 0)
                and (not self._max_fuelbed_count_threshold
                    or self._max_fuelbed_count_threshold <= 0)):
            # Configured not to truncate
            return stats

        def _insignificant(total_percent_so_far):
            if (self._insignificance_threshold
                    and self._insignificance_threshold > 0):
                return total_percent_so_far < self._insignificance_threshold

        def _too_many(fuelbeds):
            if (self._max_fuelbed_count_threshold
                    and self._max_fuelbed_count_threshold > 0):
                return len(fuelbeds) > self._max_fuelbed_count_threshold

        sorted_fuelbeds = sorted(stats.get('fuelbeds', {}).items(),
            key=lambda e: e[1]['percent'])
        total_percentage_removed = 0.0
        for fccs_id, f_dict in sorted_fuelbeds:
            if (_insignificant(total_percentage_removed + f_dict['percent'])
                    or _too_many(stats['fuelbeds']) ):
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
