"""Utility functions for the Funda webscraper."""

import re

from models.scraper_models import Address


def parse_address_line(title: str) -> Address:
    """Parse a property title string into structured address components.

    Args:
        title: The title string containing the address (e.g. "Koop: Dorpsstraat 1 1234AB Amsterdam")

    Returns:
        Address object with parsed components

    Raises:
        ValueError: If the address cannot be parsed from the title
    """
    try:
        pattern = r"(?:.*?):\s*([\w\s]+)\s+(\d+)\s*(\d{4}\s*[A-Z]{2})\s*([A-Za-z\s]+)(?:\s*\[funda\])?"
        match = re.search(pattern, title)

        if not match:
            raise ValueError("Could not parse address from title")

        return Address(
            street=match.group(1).strip(),
            number=match.group(2),
            zip_code=match.group(3).replace(" ", ""),
            city=match.group(4).strip(),
        )

    except Exception as e:
        raise ValueError(f"Failed to parse address from title: {str(e)}")


def is_valid_url(url: str) -> bool:
    """Check if a given string is a valid URL.

    Args:
        url (str): The URL string to validate

    Returns:
        bool: True if the URL is valid, False otherwise

    Example:
        >>> is_valid_url("https://www.funda.nl/koop/amsterdam/")
        True
        >>> is_valid_url("not-a-url")
        False
    """
    try:
        from urllib.parse import urlparse

        result = urlparse(url)
        # Check if scheme and netloc are present
        return all([result.scheme, result.netloc])
    except (AttributeError, ValueError):
        return False
