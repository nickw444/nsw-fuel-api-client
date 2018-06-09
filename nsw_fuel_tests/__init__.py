import datetime
import unittest
import requests_mock

from nsw_fuel import FuelCheckClient, Period, FuelCheckError
from nsw_fuel.client import API_URL_BASE


class FuelCheckClientTest(unittest.TestCase):
    def test_construction(self) -> None:
        FuelCheckClient()

    @requests_mock.Mocker()
    def test_get_fuel_prices_for_station(self, m) -> None:
        m.get('{}/station/100'.format(API_URL_BASE), json={
            'prices': [
                {
                    'fueltype': 'E10',
                    'price': 146.9,
                    'lastupdated': '02/06/2018 02:03:04',
                },
                {
                    'fueltype': 'P95',
                    'price': 150.0,
                    'lastupdated': '02/06/2018 02:03:04',
                }
            ]
        })
        client = FuelCheckClient()
        result = client.get_fuel_prices_for_station(100)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].fuel_type, 'E10')
        self.assertEqual(result[0].price, 146.9)
        self.assertEqual(result[0].last_updated, datetime.datetime(
            day=2,
            month=6,
            year=2018,
            hour=2,
            minute=3,
            second=4,
        ))

    @requests_mock.Mocker()
    def test_get_fuel_prices_within_radius(self, m) -> None:
        m.post('{}/nearby'.format(API_URL_BASE), json={
            'stations': [
                {
                    'stationid': 'SAAAAAA',
                    'brandid': 'BAAAAAA',
                    'brand': 'Cool Fuel Brand',
                    'code': 678,
                    'name': 'Cool Fuel Brand Luxembourg',
                    'address': '123 Fake Street',
                    'location': {},
                },
                {
                    'stationid': 'SAAAAAB',
                    'brandid': 'BAAAAAB',
                    'brand': 'Fake Fuel Brand',
                    'code': 679,
                    'name': 'Fake Fuel Brand Luxembourg',
                    'address': '123 Fake Street',
                    'location': {},
                },
                {
                    'stationid': 'SAAAAAB',
                    'brandid': 'BAAAAAB',
                    'brand': 'Fake Fuel Brand2',
                    'code': 880,
                    'name': 'Fake Fuel Brand2 Luxembourg',
                    'address': '123 Fake Street',
                    'location': {},
                },
            ],
            'prices': [
                {
                    'stationcode': 678,
                    'fueltype': 'P95',
                    'price': 150.9,
                    'priceunit': 'litre',
                    'description': None,
                    'lastupdated': '2018-06-02 00:46:31'
                },
                {
                    'stationcode': 678,
                    'fueltype': 'P95',
                    'price': 130.9,
                    'priceunit': 'litre',
                    'description': None,
                    'lastupdated': '2018-06-02 00:46:31'
                },
                {
                    'stationcode': 880,
                    'fueltype': 'P95',
                    'price': 155.9,
                    'priceunit': 'litre',
                    'description': None,
                    'lastupdated': '2018-06-02 00:46:31'
                }
            ],
        })

        client = FuelCheckClient()
        result = client.get_fuel_prices_within_radius(
            longitude=151.0,
            latitude=-33.0,
            radius=10,
            fuel_type='E10',
        )
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].station.code, 678)
        self.assertEqual(result[0].price.price, 150.9)

    @requests_mock.Mocker()
    def test_get_fuel_price_trends(self, m) -> None:
        m.post('{}/trends/'.format(API_URL_BASE), json={
            'Variances': [
                {'Code': 'E10', 'Period': 'Day', 'Price': 150.0},
                {'Code': 'E10', 'Period': 'Week', 'Price': 151.0},
                {'Code': 'E10', 'Period': 'Month', 'Price': 152.0},
                {'Code': 'E10', 'Period': 'Year', 'Price': 153.0},
                {'Code': 'P95', 'Period': 'Day', 'Price': 150.0},
                {'Code': 'P95', 'Period': 'Week', 'Price': 151.0},
                {'Code': 'P95', 'Period': 'Month', 'Price': 152.0},
                {'Code': 'P95', 'Period': 'Year', 'Price': 153.0},
            ],
            'AveragePrices': [
                {'Code': 'E10', 'Period': 'Day', 'Price': 150.0,
                 'Captured': '2018-06-02'},
                {'Code': 'E10', 'Period': 'Year', 'Price': 151.0,
                 'Captured': 'October 2017'}
            ],
        })

        client = FuelCheckClient()
        result = client.get_fuel_price_trends(
            longitude=151.0,
            latitude=-33.0,
            fuel_types=['E10', 'P95']
        )

        self.assertEqual(len(result.variances), 8)
        self.assertEqual(result.variances[0].price, 150.0)
        self.assertEqual(result.variances[0].period, Period.DAY)
        self.assertEqual(result.variances[0].fuel_type, 'E10')

        self.assertEqual(len(result.average_prices), 2)
        self.assertEqual(result.average_prices[0].fuel_type, 'E10')
        self.assertEqual(result.average_prices[0].period, Period.DAY)
        self.assertEqual(result.average_prices[0].captured,
                         datetime.datetime(year=2018, month=6, day=2))
        self.assertEqual(result.average_prices[0].price, 150.0)

        self.assertEqual(result.average_prices[1].period, Period.YEAR)
        self.assertEqual(result.average_prices[1].captured,
                         datetime.datetime(year=2017, month=10, day=1))

    @requests_mock.Mocker()
    def test_get_fuel_prices_for_station_error(self, m):
        m.get(
            '{}/station/21199'.format(API_URL_BASE),
            status_code=400,
            json={
                "errorDetails": [
                    {
                        "code": "E0014",
                        "description": "Invalid service station code \"21199\""
                    }
                ]
            }
        )
        client = FuelCheckClient()
        with self.assertRaises(FuelCheckError):
            client.get_fuel_prices_for_station(21199)
