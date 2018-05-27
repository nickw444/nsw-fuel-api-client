import datetime
import requests
from typing import List, Tuple

from .dto import Price, Station, Variance, AveragePrice


class FuelCheckClient():
    def _get_headers(self):
        return {
            'requesttimestamp': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }

    def get_fuel_prices_for_station(self, station: int) -> [Price]:
        response = requests.get(
            f'https://api.onegov.nsw.gov.au/FuelCheckApp/v1/fuel/prices/station/{station}',
            headers=self._get_headers())
        data = response.json()
        return [Price.deserialize(data) for data in data['prices']]

    def get_fuel_prices_within_radius(self, latitude: float, longitude: float, radius: int, fuel_type: str,
                                      brands: [str] = None) -> List[Tuple[Price, Station]]:
        if brands is None:
            brands = []
        response = requests.post('https://api.onegov.nsw.gov.au/FuelCheckApp/v1/fuel/prices/nearby', json={
            'fueltype': fuel_type,
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius,
            'brand': brands,
        }, headers=self._get_headers())
        data = response.json()
        stations = {station['code']: Station.deserialize(station) for station in data['stations']}
        station_prices = []
        for serialized_price in data['prices']:
            price = Price.deserialize(serialized_price)
            station_prices.append((price, stations[price.station_code]))

        return station_prices

    def get_fuel_price_trends(self, latitude, longitude, fuel_types: [str]):
        response = requests.post('https://api.onegov.nsw.gov.au/FuelCheckApp/v1/fuel/prices/trends/', json={
            'location': {
                'latitude': latitude,
                'longitude': longitude,
            },
            'fueltypes': [{'code': type} for type in fuel_types],
        }, headers=self._get_headers())
        data = response.json()
        return {
            'variances': [Variance.deserialize(variance) for variance in data['Variances']],
            'average_prices': [AveragePrice.deserialize(avg_price) for avg_price in data['AveragePrices']],
        }
