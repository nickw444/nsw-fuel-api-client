from datetime import datetime
from enum import Enum


class Price(object):
    def __init__(self, fuel_type: str, price: float, last_updated, price_unit: str, station_code):
        self.fuel_type = fuel_type
        self.price = price
        self.last_updated = last_updated
        self.price_unit = price_unit
        self.station_code = station_code

    @classmethod
    def deserialize(cls, data: dict):
        return Price(
            fuel_type=data['fueltype'],
            price=data['price'],
            last_updated=data['lastupdated'],
            price_unit=data.get('priceunit'),
            station_code=data.get('stationcode')
        )

    def __repr__(self):
        return '<Price fuel_type={} price={}>'.format(self.fuel_type, self.price)


class Station(object):
    def __init__(self, id, brand, code, name, address):
        self.id = id
        self.brand = brand
        self.code = code
        self.name = name
        self.address = address

    @classmethod
    def deserialize(cls, data: dict):
        return Station(
            id=data['stationid'],
            brand=data['brand'],
            code=data['code'],
            name=data['name'],
            address=data['address']
        )

    def __repr__(self):
        return '<Station id={} code={} brand={} name={}>'.format(self.id, self.code, self.brand, self.name)


class Period(Enum):
    DAY = 'Day'
    MONTH = 'Month'
    YEAR = 'Year'
    WEEK = 'Week'


class Variance(object):
    def __init__(self, fuel_type, period, price):
        self.fuel_type = fuel_type
        self.period = period
        self.price = price

    @classmethod
    def deserialize(cls, data: dict):
        return Variance(
            fuel_type=data['Code'],
            period=Period(data['Period']),
            price=data['Price'],
        )

    def __repr__(self):
        return '<Variance fuel_type={} period={} price={}>'.format(
            self.fuel_type,
            self.period,
            self.price,
        )


class AveragePrice(object):
    def __init__(self, fuel_type, period, price, captured):
        self.fuel_type = fuel_type
        self.period = period
        self.price = price
        self.captured = captured

    @classmethod
    def deserialize(cls, data: dict):
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

    def __repr__(self):
        return '<AveragePrice fuel_type={} period={} price={} captured={}>'.format(
            self.fuel_type,
            self.period,
            self.price,
            self.captured
        )
