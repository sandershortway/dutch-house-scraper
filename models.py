"""Data models for the Funda webscraper."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Website(Enum):
    FUNDA = "funda"
    HUISLIJN = "huislijn"


@dataclass
class Address:
    """Data class representing a Dutch property address."""

    street: str = None
    number: str = None
    city: str = None
    zip_code: str = None
    neighbourhood: Optional[str] = None
    province: Optional[str] = None
    country: str = "The Netherlands"


@dataclass
class Property:
    """Data class representing Dutch property information."""

    energylabel: str = None
    living_area: int = None
    num_rooms: int = None
    build_year: int = None
    type: str = None


@dataclass
class Price:
    """Data class representing price data for a listing."""

    asking_price: float = None
    asking_price_per_square_meter: float = None
    sale_price: Optional[float] = None


@dataclass
class Listing:
    """Data class representing a Dutch property listing."""

    address: Address = None
    property: Property = None
    price: Price = None
    website: Website = None
    url: str = None
