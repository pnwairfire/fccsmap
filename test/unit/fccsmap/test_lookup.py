from py.test import raises

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
                    'grid_cells': 4,
                    'percent': 100.0
                }
            },
           'sampled_area': 4014629.570946319,
           'sampled_grid_cells': 4,
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
                '319': {'grid_cells': 4, 'percent': 18.18181818181818},
                '41': {'grid_cells': 1, 'percent': 4.545454545454545},
                '52': {'grid_cells': 10, 'percent': 45.45454545454545},
                '60': {'grid_cells': 7, 'percent': 31.818181818181813}
            },
            'sampled_area': 36128384.2273902,
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
                '24': {'grid_cells': 4, 'percent': 80.0},
                '52': {'grid_cells': 1, 'percent': 20.0}
            },
            'sampled_area': 4014605.673739771,
            'sampled_grid_cells': 5,
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
            'sampled_area': 8029771.678782582,
            'fuelbeds': {
                '4': {'grid_cells': 2, 'percent': 20.0},
                '60': {'grid_cells': 2, 'percent': 20.0},
                '52': {'grid_cells': 2, 'percent': 20.0},
                '24': {'grid_cells': 4, 'percent': 40.0}
            }, 'units': 'm^2', 'sampled_grid_cells': 10}
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
            'sampled_area': 72257497.56205451,
            'sampled_grid_cells': 72,
            'units': 'm^2',
            'fuelbeds': {
                '319': {'grid_cells': 5, 'percent': 10.869565217391305},
                '60': {'grid_cells': 7, 'percent': 15.217391304347826},
                '52': {'grid_cells': 33, 'percent': 71.73913043478261},
                '41': {'grid_cells': 1, 'percent': 2.1739130434782608}
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
            'area': 8217580424.304997,
            'grid_cells': 8219,
            'fuelbeds': {
                '237': {'percent': 10.356963298139767, 'grid_cells': 824},
                '24': {'percent': 0.025138260432378077, 'grid_cells': 2},
                '319': {'percent': 2.551533433886375, 'grid_cells': 203},
                '41': {'percent': 2.7275012569130217, 'grid_cells': 217},
                '305': {'percent': 0.4147812971342383, 'grid_cells': 33},
                '60': {'percent': 4.462041226747108, 'grid_cells': 355},
                '4': {'percent': 0.03770739064856712, 'grid_cells': 3},
                '21': {'percent': 0.012569130216189038, 'grid_cells': 1},
                '208': {'percent': 0.9049773755656108, 'grid_cells': 72},
                '22': {'percent': 0.5656108597285068, 'grid_cells': 45},
                '238': {'percent': 4.3740573152337845, 'grid_cells': 348},
                '59': {'percent': 10.985419808949219, 'grid_cells': 874},
                '9': {'percent': 11.65158371040724, 'grid_cells': 927},
                '70': {'percent': 0.6033182503770739, 'grid_cells': 48},
                '63': {'percent': 1.0809451985922571, 'grid_cells': 86},
                '8': {'percent': 0.0628456510809452, 'grid_cells': 5},
                '28': {'percent': 0.025138260432378077, 'grid_cells': 2},
                '61': {'percent': 13.763197586726998, 'grid_cells': 1095},
                '52': {'percent': 35.39467068878833, 'grid_cells': 2816}
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
                "208": {
                    "grid_cells": 72,
                    "percent": 0.9048636420761593
                },
                "8": {
                    "grid_cells": 5,
                    "percent": 0.06283775292195551
                },
                "305": {
                    "grid_cells": 33,
                    "percent": 0.4147291692849064
                },
                "28": {
                    "grid_cells": 2,
                    "percent": 0.025135101168782203
                },
                "41": {
                    "grid_cells": 217,
                    "percent": 2.727158476812869
                },
                "24": {
                    "grid_cells": 2,
                    "percent": 0.025135101168782203
                },
                "63": {
                    "grid_cells": 86,
                    "percent": 1.0808093502576348
                },
                "61": {
                    "grid_cells": 1095,
                    "percent": 13.761467889908257
                },
                "60": {
                    "grid_cells": 355,
                    "percent": 4.461480457458841
                },
                "237": {
                    "grid_cells": 824,
                    "percent": 10.355661681538267
                },
                "4": {
                    "grid_cells": 3,
                    "percent": 0.037702651753173305
                },
                "319": {
                    "grid_cells": 203,
                    "percent": 2.5512127686313937
                },
                "52": {
                    "grid_cells": 2817,
                    "percent": 35.402789996229735
                },
                "21": {
                    "grid_cells": 1,
                    "percent": 0.012567550584391102
                },
                "9": {
                    "grid_cells": 927,
                    "percent": 11.650119391730552
                },
                "238": {
                    "grid_cells": 348,
                    "percent": 4.373507603368103
                },
                "59": {
                    "grid_cells": 874,
                    "percent": 10.984039210757823
                },
                "22": {
                    "grid_cells": 45,
                    "percent": 0.5655397762975996
                },
                "70": {
                    "grid_cells": 48,
                    "percent": 0.6032424280507729
                }
            },
            "area": 16273677189.8695
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
