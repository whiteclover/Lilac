import unittest

from lilac.util import json_encode, json_decode


class TestJsonify(unittest.TestCase):

    def test_custom_json(self):

        class Dummy(object):

            def as_json(self):
                return [1, 3, 3]

        self.assertEqual(dumps(Dummy()), '[1, 3, 3]')