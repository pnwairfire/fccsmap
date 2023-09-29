from pytest import raises

from fccsmap.lookup import FccsLookUp


class TestFccsLookUp(object):
    """Tests for FccsLookUp.look_up

    NOTE: Test data were generated using FccsLookUp itself.
    So, the TestFccsLookUp serves as a regression test, making sure
    future updates don't break the existing behavior.
    (The output data were spot-checked to ensure that the fuelbed do make
    sense for each location.)
    """

    def setup(self):
        self._lookup = FccsLookUp()

    def test_point(self):
        geo_data = {
            "type": "Point",
            # hills east of Methow valley
            "coordinates": [-119.877732, 48.4255591]
        }
        expected = {
            'fuelbeds': {
                '52': {
                    'percent': 100.00000000000001,
                    'grid_cells': 34
                }
            },
            'sampled_grid_cells': 37,
            'sampled_area': 36131660.998113036,
            'units': 'm^2'
        }

        assert self._lookup.look_up(geo_data) == expected

    def test_point_in_water(self):
        geo_data = {
            "type": "Point",
            # in lake chelan
            "coordinates": [-120.3606708, 48.0364064]
        }
        expected = {
            'fuelbeds': {
                '319': {'grid_cells': 4, 'percent': 19.047619047619047},
                '52': {'grid_cells': 10, 'percent': 47.61904761904762},
                '60': {'grid_cells': 7, 'percent': 33.33333333333333}
            },
            'sampled_area': 36128384.22738944,
            'sampled_grid_cells': 36,
            'units': 'm^2'
        }
        assert self._lookup.look_up(geo_data) == expected

    def test_multipoint_one(self):
        geo_data = {
            "type": "MultiPoint",
            "coordinates": [
                # hills east of Methow valley
                [-119.8, 48.4]
            ]
        }
        expected = {
            'fuelbeds': {
                '24': {'grid_cells': 25, 'percent': 67.56756756756756},
                '52': {'grid_cells': 12, 'percent': 32.432432432432435}
            },
            'sampled_grid_cells': 37,
            'sampled_area': 36131445.92730406,
            'units': 'm^2'
        }
        assert self._lookup.look_up(geo_data) == expected

    def test_multipoint_two(self):
        geo_data = {
            "type": "MultiPoint",
            "coordinates": [
                [-119.8, 48.4],
                [-119.0, 49.0]
            ]
        }
        expected = {
            'fuelbeds': {
                '4': {'grid_cells': 12, 'percent': 16.666666666666668},
                '60': {'grid_cells': 11, 'percent': 15.277777777777779},
                '52': {'grid_cells': 24, 'percent': 33.333333333333336},
                '24': {'grid_cells': 25, 'percent': 34.72222222222222}
            },
            'sampled_grid_cells': 72,
            'sampled_area': 72267934.74002303,
            'units': 'm^2',
        }
        assert self._lookup.look_up(geo_data) == expected

    def test_multipoint_in_water(self):
        geo_data = {
            "type": "MultiPoint",
            # in lake chelan
            "coordinates": [
                [-120.3606708, 48.0364064],
                [-120.5059529, 48.1229493]
            ]
        }
        expected = {
            'sampled_area': 72257497.56205192,
            'sampled_grid_cells': 72,
            'units': 'm^2',
            'fuelbeds': {
                '319': {'grid_cells': 5, 'percent': 11.111111111111112},
                '60': {'grid_cells': 7, 'percent': 15.555555555555557},
                '52': {'grid_cells': 33, 'percent': 73.33333333333334}
            }
        }
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
        expected = {
            'units': 'm^2',
            'area': 8217580424.304947,
            'grid_cells': 8219,
            'fuelbeds': {
                '237': {'grid_cells': 824, 'percent': 11.382787677856056},
                '238': {'grid_cells': 348, 'percent': 4.807293825113965},
                '52': {'grid_cells': 2816, 'percent': 38.90040060781876},
                '59': {'grid_cells': 874, 'percent': 12.073490813648293},
                '60': {'grid_cells': 355, 'percent': 4.903992264124879},
                '61': {'grid_cells': 1095, 'percent': 15.12639867384998},
                '9': {'grid_cells': 927, 'percent': 12.805636137588065}
            }
        }
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
        expected = {
            "units": "m^2",
            "grid_cells": 8220,
            "fuelbeds": {
                '237': {'grid_cells': 824, 'percent': 11.381215469613258},
                '238': {'grid_cells': 348, 'percent': 4.806629834254142},
                '52': {'grid_cells': 2817, 'percent': 38.90883977900552},
                '59': {'grid_cells': 874, 'percent': 12.071823204419887},
                '60': {'grid_cells': 355, 'percent': 4.903314917127071},
                '61': {'grid_cells': 1095, 'percent': 15.124309392265191},
                '9': {'grid_cells': 927, 'percent': 12.803867403314916}
            },
            "area": 16273677189.869366
        }
        assert self._lookup.look_up(geo_data) == expected


class TestFccsLookUpTransformPoints(object):

    def setup(self):
        self._lookup = FccsLookUp()

    def test_point(self):
        geo_data = {
            "type": "Point",
            # hills east of Methow valley
            "coordinates": [-119.877732, 48.4255591]
        }
        expected = {
            'coordinates': [
                [
                    [
                        [-119.89126896768474, 48.416550090990995],
                        [-119.89126896768474, 48.43456810900901],
                        [-119.86419503231525, 48.43456810900901],
                        [-119.86419503231525, 48.416550090990995]
                    ]
                ]
            ],
            'type': 'MultiPolygon'
        }
        assert self._lookup._transform_points(geo_data, 1) == expected

    def test_multi_point(self):
        geo_data = {
            "type": "MultiPoint",
            "coordinates": [
                [-119.877732, 48.4255591],
                [-119.7, 48.5]
            ]
        }
        expected = {
            'coordinates': [
                [
                    [
                        [-119.89126896768474, 48.416550090990995],
                        [-119.89126896768474, 48.43456810900901],
                        [-119.86419503231525, 48.43456810900901],
                        [-119.86419503231525, 48.416550090990995]
                    ]
                ],
                [
                    [
                        [-119.71355683559308, 48.490990990990994],
                        [-119.71355683559308, 48.509009009009006],
                        [-119.68644316440692, 48.509009009009006],
                        [-119.68644316440692, 48.490990990990994]
                    ]
                ]
            ],
            'type': 'MultiPolygon'
        }
        assert self._lookup._transform_points(geo_data, 1) == expected

class TestFccsLookUpHasHighPercentOfIgnored(object):

    def setup(self):
        self._lookup = FccsLookUp()

    def test_one_good(self):
        stats = {
            'fuelbeds': {
                '41': {
                    'percent': 100.0,
                    'grid_cells': 1
                }
            },
            'grid_cells': 10
        }
        assert self._lookup._has_high_percent_of_ignored(stats) == False

    def test_two_good(self):
        stats = {
            'fuelbeds': {
                '41': {
                    'percent': 25.0,
                    'grid_cells': 1
                },
                '60': {
                    'percent': 75.0,
                    'grid_cells': 3
                }
            },
            'grid_cells': 10
        }
        assert self._lookup._has_high_percent_of_ignored(stats) == False

    def test_mixture(self):
        stats = {
            'fuelbeds': {
                '900': {
                    'percent': 40.0,
                    'grid_cells': 4
                },
                '0': {
                    'percent': 20.0,
                    'grid_cells': 2
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
        assert self._lookup._has_high_percent_of_ignored(stats) == False

    def test_one_ignored(self):
        stats = {
            'fuelbeds': {
                '900': {
                    'percent': 100.0,
                    'grid_cells': 3
                }
            },
            'grid_cells': 10
        }
        assert self._lookup._has_high_percent_of_ignored(stats) == True

    def test_two_ignored(self):
        stats = {
            'fuelbeds': {
                '900': {
                    'percent': 60.0,
                    'grid_cells': 3
                },
                '0': {
                    'percent': 40.0,
                    'grid_cells': 2
                }
            },
            'grid_cells': 10
        }
        assert self._lookup._has_high_percent_of_ignored(stats) == True


class TestFccsLookupComputeTotalPercentIgnored(object):

    def setup(self):
        self._lookup = FccsLookUp()

    def test_one_good(self):
        stats = {
            'fuelbeds': {
                '41': {
                    'percent': 100.0,
                    'grid_cells': 1
                }
            },
            'grid_cells': 10
        }
        assert self._lookup._compute_total_percent_ignored(stats) == 0.0

    def test_two_good(self):
        stats = {
            'fuelbeds': {
                '41': {
                    'percent': 25.0,
                    'grid_cells': 1
                },
                '60': {
                    'percent': 75.0,
                    'grid_cells': 3
                }
            },
            'grid_cells': 10
        }
        assert self._lookup._compute_total_percent_ignored(stats) == 0.0

    def test_mixture(self):
        stats = {
            'fuelbeds': {
                '900': {
                    'percent': 40.0,
                    'grid_cells': 4
                },
                '0': {
                    'percent': 20.0,
                    'grid_cells': 2
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
        assert self._lookup._compute_total_percent_ignored(stats) == 60.0

    def test_one_ignored(self):
        stats = {
            'fuelbeds': {
                '900': {
                    'percent': 100.0,
                    'grid_cells': 3
                }
            },
            'grid_cells': 10
        }
        assert self._lookup._compute_total_percent_ignored(stats) == 100.0

    def test_two_ignored(self):
        stats = {
            'fuelbeds': {
                '900': {
                    'percent': 60.0,
                    'grid_cells': 3
                },
                '0': {
                    'percent': 40.0,
                    'grid_cells': 2
                }
            },
            'grid_cells': 10
        }
        assert self._lookup._compute_total_percent_ignored(stats) == 100.0


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


class TestFccsLookupRemoveInsignificant(object):

    def setup(self):
        self._lookup = FccsLookUp()

    def test_empty_fuelbeds(self):
        stats = {
            "fuelbeds": {},
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
        assert self._lookup._remove_insignificant(stats) == expected

    def test_none_removed(self):
        stats = {
            "fuelbeds": {
                "32": {"percent": 50, "grid_cells": 2},
                "41": {"percent": 50, "grid_cells": 2}
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        expected = {
            "fuelbeds": {
                "32": {"percent": 50, "grid_cells": 2},
                "41": {"percent": 50, "grid_cells": 2}
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        assert self._lookup._remove_insignificant(stats) == expected

    def test_two_removed(self):
        stats = {
            "fuelbeds": {
                "24": {"percent": 48, "grid_cells": 2 },
                "1": {"percent": 48, "grid_cells": 2},
                "13": {"percent": 2, "grid_cells": 2},
                "41": {"percent": 2, "grid_cells": 2}
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        expected = {
            "fuelbeds": {
                "24": {"percent": 50, "grid_cells": 2},
                "1": {"percent": 50, "grid_cells": 2}
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        assert self._lookup._remove_insignificant(stats) == expected


class TestFccsLookupReadjustPercentages(object):

    def setup(self):
        self._lookup = FccsLookUp()

    def test_empty(self):
        stats = {
            "fuelbeds": {},
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
        assert self._lookup._readjust_percentages(stats, 0) == expected

    def test_one_none_adjusted(self):
        stats = {
            "fuelbeds": {
                "32": {"percent": 100, "grid_cells": 2}
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        expected = {
            "fuelbeds": {
                "32": {"percent": 100, "grid_cells": 2}
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        assert self._lookup._readjust_percentages(stats, 0) == expected

    def test_one_adjusted(self):
        stats = {
            "fuelbeds": {
                "32": {"percent": 50, "grid_cells": 2}
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        expected = {
            "fuelbeds": {
                "32": {"percent": 100, "grid_cells": 2}
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        assert self._lookup._readjust_percentages(stats, 50) == expected

    def test_multiple_none_adjusted(self):
        stats = {
            "fuelbeds": {
                "32": {"percent": 50, "grid_cells": 2},
                "41": {"percent": 50, "grid_cells": 2}
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        expected = {
            "fuelbeds": {
                "32": {"percent": 50, "grid_cells": 2},
                "41": {"percent": 50, "grid_cells": 2}
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        assert self._lookup._readjust_percentages(stats, 0) == expected

    def test_multiple_some_adjusted(self):
        stats = {
            "fuelbeds": {
                "32": {"percent": 40, "grid_cells": 2},
                "41": {"percent": 40, "grid_cells": 2}
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        expected = {
            "fuelbeds": {
                "32": {"percent": 50, "grid_cells": 2},
                "41": {"percent": 50, "grid_cells": 2}
            },
            "sampled_area": 1,
            "sampled_grid_cells": 1,
            "units": "m^2"
        }
        assert self._lookup._readjust_percentages(stats, 20) == expected