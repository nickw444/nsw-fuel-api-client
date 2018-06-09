import datetime
from typing import List, Optional, NamedTuple

import requests

from .dto import Price, Station, Variance, AveragePrice, FuelCheckError

API_URL_BASE = 'https://api.onegov.nsw.gov.au/FuelCheckApp/v1/fuel/prices'

PriceTrends = NamedTuple('PriceTrends', [
    ('variances', List[Variance]),
    ('average_prices', List[AveragePrice])
])

StationPrice = NamedTuple('StationPrice', [
    ('price', Price),
    ('station', Station)
])


class FuelCheckClient():
    def __init__(self, timeout: Optional[int] = 10) -> None:
        self._timeout = timeout

    def _get_headers(self) -> dict:
        return {
            'requesttimestamp': datetime.datetime.now().strftime(
                '%d/%m/%Y %H:%M:%S')
        }

    def get_fuel_prices_for_station(self, station: int) -> List[Price]:
        """Gets the fuel prices for a specific fuel station."""
        response = requests.get(
            '{}/station/{}'.format(API_URL_BASE, station),
            headers=self._get_headers(),
            timeout=self._timeout,
        )

        if not response.ok:
            raise FuelCheckError.create(response)

        data = response.json()
        return [Price.deserialize(data) for data in data['prices']]

    def get_fuel_prices_within_radius(
            self, latitude: float, longitude: float, radius: int,
            fuel_type: str, brands: Optional[List[str]] = None
    ) -> List[StationPrice]:
        """Gets all the fuel prices within the specified radius."""

        if brands is None:
            brands = []
        response = requests.post(
            '{}/nearby'.format(API_URL_BASE),
            json={
                'fueltype': fuel_type,
                'latitude': latitude,
                'longitude': longitude,
                'radius': radius,
                'brand': brands,
            },
            headers=self._get_headers(),
            timeout=self._timeout,
        )

        if not response.ok:
            raise FuelCheckError.create(response)

        data = response.json()
        stations = {
            station['code']: Station.deserialize(station)
            for station in data['stations']
        }
        station_prices = []  # type: List[StationPrice]
        for serialized_price in data['prices']:
            price = Price.deserialize(serialized_price)
            station_prices.append(StationPrice(
                price=price,
                station=stations[price.station_code]
            ))

        return station_prices

    def get_fuel_price_trends(self, latitude: float, longitude: float,
                              fuel_types: List[str]) -> PriceTrends:
        """Gets the fuel price trends for the given location and fuel types."""
        response = requests.post(
            '{}/trends/'.format(API_URL_BASE),
            json={
                'location': {
                    'latitude': latitude,
                    'longitude': longitude,
                },
                'fueltypes': [{'code': type} for type in fuel_types],
            },
            headers=self._get_headers(),
            timeout=self._timeout,
        )

        if not response.ok:
            raise FuelCheckError.create(response)

        data = response.json()
        return PriceTrends(
            variances=[
                Variance.deserialize(variance)
                for variance in data['Variances']
            ],
            average_prices=[
                AveragePrice.deserialize(avg_price)
                for avg_price in data['AveragePrices']
            ]
        )
