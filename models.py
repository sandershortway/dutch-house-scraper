"""Data models for the Funda webscraper."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class HouseType(Enum):
    APARTMENT: str = "Apartment"
    HOUSE: str = "House"


@dataclass
class Address:
    """Data class representing a Dutch property address."""

    street: str = None
    number: str = None
    city: str = None
    zip_code: str = None
    neighbourhood: Optional[str] = None
    province: Optional[str] = None
    type: Optional[str] = None
    country: str = "The Netherlands"


@dataclass
class Price:
    """Data class representing price data for a listing."""

    asking_price: float = None
    asking_price_per_square_meter: float = None
    sale_price: Optional[float] = None
