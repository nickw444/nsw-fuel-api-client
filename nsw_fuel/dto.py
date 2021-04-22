from datetime import datetime
from enum import Enum
from typing import Optional, List, Any, Dict

from requests import Response


class Price(object):
    def __init__(self, fuel_type: str, price: float,
                 last_updated: Optional[datetime], price_unit: Optional[str],
                 station_code: Optional[int]) -> None:
        self.fuel_type = fuel_type
        self.price = price
        self.last_updated = last_updated
        self.price_unit = price_unit
        self.station_code = station_code

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Price':

        # Stupid API has two different date representations! :O
        lastupdated = None
        try:
            lastupdated = datetime.strptime(
                data['lastupdated'], '%d/%m/%Y %H:%M:%S')
        except ValueError:
            pass
        try:
            lastupdated = datetime.strptime(
                data['lastupdated'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass

        station_code = None # type: Optional[int]
        if 'stationcode' in data:
            station_code = int(data['stationcode'])

        return Price(
            fuel_type=data['fueltype'],
            price=data['price'],
            last_updated=lastupdated,
            price_unit=data.get('priceunit'),
            station_code=station_code
        )

    def __repr__(self) -> str:
        return '<Price fuel_type={} price={}>'.format(
            self.fuel_type, self.price)


class Station(object):
    def __init__(self, id: Optional[str], brand: str, code: int,
                 name: str, address: str) -> None:
        self.id = id
        self.brand = brand
        self.code = code
        self.name = name
        self.address = address

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Station':
        return Station(
            id=data.get('stationid'),
            brand=data['brand'],
            code=int(data['code']),
            name=data['name'],
            address=data['address']
        )

    def __repr__(self) -> str:
        return '<Station id={} code={} brand={} name={}>'.format(
            self.id, self.code, self.brand, self.name)


class Period(Enum):
    DAY = 'Day'
    MONTH = 'Month'
    YEAR = 'Year'
    WEEK = 'Week'


class Variance(object):
    def __init__(self, fuel_type: str, period: Period, price: float) -> None:
        self.fuel_type = fuel_type
        self.period = period
        self.price = price

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Variance':
        return Variance(
            fuel_type=data['Code'],
            period=Period(data['Period']),
            price=data['Price'],
        )

    def __repr__(self) -> str:
        return '<Variance fuel_type={} period={} price={}>'.format(
            self.fuel_type,
            self.period,
            self.price,
        )


class AveragePrice(object):
    def __init__(self, fuel_type: str, period: Period, price: float,
                 captured: datetime) -> None:
        self.fuel_type = fuel_type
        self.period = period
        self.price = price
        self.captured = captured

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'AveragePrice':
        period = Period(data['Period'])

        captured_raw = data['Captured']
        if period in [Period.DAY, Period.WEEK, Period.MONTH]:
            captured = datetime.strptime(captured_raw, '%Y-%m-%d')
        elif period == Period.YEAR:
            captured = datetime.strptime(captured_raw, '%B %Y')
        else:
            captured = captured_raw

        return AveragePrice(
            fuel_type=data['Code'],
            period=period,
            price=data['Price'],
            captured=captured,
        )

    def __repr__(self) -> str:
        return ('<AveragePrice fuel_type={} period={} price={} '
                'captured={}>').format(
            self.fuel_type,
            self.period,
            self.price,
            self.captured
        )


class FuelType(object):
    def __init__(self, code: str, name: str) -> None:
        self.code = code
        self.name = name

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'FuelType':
        return FuelType(
            code=data['code'],
            name=data['name']
        )


class TrendPeriod(object):
    def __init__(self, period: str, description: str) -> None:
        self.period = period
        self.description = description

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'TrendPeriod':
        return TrendPeriod(
            period=data['period'],
            description=data['description']
        )


class SortField(object):
    def __init__(self, code: str, name: str) -> None:
        self.code = code
        self.name = name

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'SortField':
        return SortField(
            code=data['code'],
            name=data['name']
        )


class GetReferenceDataResponse(object):
    def __init__(self, stations: List[Station], brands: List[str],
                 fuel_types: List[FuelType], trend_periods: List[TrendPeriod],
                 sort_fields: List[SortField]) -> None:
        self.stations = stations
        self.brands = brands
        self.fuel_types = fuel_types
        self.trend_periods = trend_periods
        self.sort_fields = sort_fields

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'GetReferenceDataResponse':
        stations = [Station.deserialize(x) for x in data['stations']['items']]
        brands = [x['name'] for x in data['brands']['items']]
        fuel_types = [FuelType.deserialize(x) for x in
                      data['fueltypes']['items']]
        trend_periods = [TrendPeriod.deserialize(x) for x in
                         data['trendperiods']['items']]
        sort_fields = [SortField.deserialize(x) for x in
                       data['sortfields']['items']]

        return GetReferenceDataResponse(
            stations=stations,
            brands=brands,
            fuel_types=fuel_types,
            trend_periods=trend_periods,
            sort_fields=sort_fields
        )

    def __repr__(self) -> str:
        return ('<GetReferenceDataResponse stations=<{} stations>>').format(
            len(self.stations)
        )


class GetFuelPricesResponse(object):
    def __init__(self, stations: List[Station], prices: List[Price]) -> None:
        self.stations = stations
        self.prices = prices

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'GetFuelPricesResponse':
        stations = [Station.deserialize(x) for x in data['stations']]
        prices = [Price.deserialize(x) for x in data['prices']]
        return GetFuelPricesResponse(
            stations=stations,
            prices=prices
        )


class FuelCheckError(Exception):
    def __init__(self, error_code: Optional[str] = None,
                 description: Optional[str] = None) -> None:
        super(FuelCheckError, self).__init__(description)
        self.error_code = error_code

    @classmethod
    def create(cls, response: Response) -> 'FuelCheckError':
        error_code = None
        description = response.text
        try:
            data = response.json()
            if 'errorDetails' in data:
                error_details = data['errorDetails']
                if type(error_details) == list and len(error_details) > 0:
                    error_details = error_details[0]
                    error_code = error_details.get('code')
                    description = error_details.get('description')
                elif type(error_details) == dict:
                    error_code = error_details.get('code')
                    description = error_details.get('message')

        except ValueError:
            pass

        return FuelCheckError(
            error_code=error_code,
            description=description
        )
