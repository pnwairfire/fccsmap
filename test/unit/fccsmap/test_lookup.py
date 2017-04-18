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