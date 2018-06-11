import unittest

from nsw_fuel import FuelCheckClient


class FuelCheckClientIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.client = FuelCheckClient()

    def test_get_reference_data(self) -> None:
        response = self.client.get_reference_data()
        self.assertGreater(len(response.stations), 1500)

    def test_get_fuel_prices(self) -> None:
        response = self.client.get_fuel_prices()
        self.assertGreater(len(response.stations), 1500)
        self.assertGreater(len(response.prices), 1500)

    def test_get_fuel_prices_for_station(self) -> None:
        response = self.client.get_reference_data()
        station_id = response.stations[0].code

        response = self.client.get_fuel_prices_for_station(station_id)
        self.assertGreaterEqual(len(response), 1)
