from py.test import raises

from fccsmap.lookup import FccsLookUp

class TestFccsLookUp(object):
    """Tests for FccsLookUp.look_up
    """

    def setup(self):
        self._lookup = FccsLookUp()

    def test_point(self):
        geo_data = {
            "type": "Point",
            # hills east of Methow valley
            "coordinates": [-119.877732, 48.4255591]
        }
        expected = {}
        assert self._lookup.look_up(geo_data) == expected

    def test_point_in_water(self):
        geo_data = {
            "type": "Point",
            # in lake chelan
            "coordinates": [-120.3606708, 48.0364064]
        }
        expected = {}
        assert self._lookup.look_up(geo_data) == expected

    def test_multipoint_one(self):
        geo_data = {
            "type": "MultiPoint",
            "coordinates": [
                # hills east of Methow valley
                [-119.8, 48.4]
            ]
        }
        expected = {}
        assert self._lookup.look_up(geo_data) == expected

    def test_multipoint_two(self):
        geo_data = {
            "type": "MultiPoint",
            "coordinates": [
                [-119.8, 48.4],
                [-119.0, 49.0]
            ]
        }
        expected = {}
        assert self._lookup.look_up(geo_data) == expected

    def test_multipoint_in_water(self):
        geo_data = {
            "type": "Point",
            # in lake chelan
            "coordinates": [
                [-120.3606708, 48.0364064],
                [-120.5059529, 48.1229493]
            ]
        }
        expected = {}
        assert self._lookup.look_up(geo_data) == expected

    def test_polygon(self):
        geo_data = {
            "type": "Polygon",
            # in and around lake chelan
            "coordinates": [
                [
                    [-120.0, 48.0],
                    [-121.0, 48.0],
                    [-121.0, 49.0],
                    [-120.0, 49.0],
                    [-120.0, 48.0],
                ]
            ]
        }
        expected = {}
        assert self._lookup.look_up(geo_data) == expected

    def test_multipolygon(self):
        geo_data = {
            "type": "MultiPolygon",
            # in and around lake chelan
            "coordinates": [
                [
                    [
                        [-120.0, 48.0],
                        [-121.0, 48.0],
                        [-121.0, 49.0],
                        [-120.0, 49.0],
                        [-120.0, 48.0],
                    ]
                ],
                [
                    [
                        [-121.0, 49.0],
                        [-122.0, 49.0],
                        [-122.0, 50.0],
                        [-121.0, 50.0],
                        [-121.0, 49.0],
                    ]
                ]
            ]
        }
        expected = {}
        assert self._lookup.look_up(geo_data) == expected

class TestFccsLookUpTransformPoints(object):

    def test_point(self):
        pass

    def test_multi_point(self):
        pass

class TestFccsLookUpHasHighPercentOfIgnored(object):

    def test_one_good(self):
        pass

    def test_two_good(self):
        pass

    def test_mixture(self):
        pass

    def test_one_ignored(self):
        pass

    def test_one_ignored(self):
        pass

class TestFccsLookupComputeTotalPercentIgnored(object):

    def test_one_good(self):
        pass

    def test_two_good(self):
        pass

    def test_mixture(self):
        pass

    def test_one_ignored(self):
        pass

    def test_one_ignored(self):
        pass

class TestFccsLookupComputePercentages(object):

    def setup(self):
        self._lookup = FccsLookUp()

    def test_none(self):
        # TODO: figure out what shapely would return if no hits
        pass

    def test_one(self):
        stats = [
            {
                'min': 24.0,
                '__fid__': 0,
                'mean': 24.0,
                'counts': {
                    24: 1
                },
                'count': 1,
                'max': 24.0
            }
        ]
        expected = {
            'fuelbeds': {
                '24': {
                    'percent': 100.0,
                    'grid_cells': 1
                }
            },
            'grid_cells': 1
        }
        assert self._lookup._compute_percentages(stats) == expected

    def test_multiple(self):
        stats = [
            {
                'min': 41.0,
                '__fid__': 0,
                'mean': 562.1,
                'counts': {
                    900: 6,
                    41: 1,
                    60: 3
                },
                'count': 14,
                'max': 900.0
            }
        ]
        expected = {
            'fuelbeds': {
                '900': {
                    'percent': 60.0,
                    'grid_cells': 6
                },
                '41': {
                    'percent': 10.0,
                    'grid_cells': 1
                },
                '60': {
                    'percent': 30.0,
                    'grid_cells': 3
                }
            },
            'grid_cells': 10
        }
        assert self._lookup._compute_percentages(stats) == expected


class TestFccsLookupRemoveIgnored(object):

    def setup(self):
        self._lookup = FccsLookUp()

    def test_no_ignored(self):
        stats = {
            "fuelbeds": {
                "32": {
                    "percent": 50,
                    "grid_cells": 2
                },
                "41": {
                    "percent": 50,
                    "grid_cells": 2
                }
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        expected = {
            "fuelbeds": {
                "32": {
                    "percent": 50,
                    "grid_cells": 2
                },
                "41": {
                    "percent": 50,
                    "grid_cells": 2
                }
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        assert self._lookup._remove_ignored(stats) == expected

    def test_all_ignored(self):
        stats = {
            "fuelbeds": {
                "900": {
                    "percent": 50,
                    "grid_cells": 2
                },
                "0": {
                    "percent": 50,
                    "grid_cells": 2
                }
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        expected = {
            "fuelbeds": {},
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        assert self._lookup._remove_ignored(stats) == expected

    def test_mixed(self):
        stats = {
            "fuelbeds": {
                "900": {
                    "percent": 50,
                    "grid_cells": 2
                },
                "41": {
                    "percent": 50,
                    "grid_cells": 2
                }
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        expected = {
            "fuelbeds": {
                "41": {
                    "percent": 100,
                    "grid_cells": 2
                }
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        assert self._lookup._remove_ignored(stats) == expected
