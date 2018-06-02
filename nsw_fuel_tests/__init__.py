import unittest

from nsw_fuel import FuelCheckClient


class FuelCheckClientTest(unittest.TestCase):
    def test_construction(self):
        FuelCheckClient()
