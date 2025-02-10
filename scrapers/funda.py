"""Module for scraping Funda property listing website."""

import json
import re
from typing import Any, Dict, Optional

from scrapers.base import BaseScraper
from utils.utils import parse_address_line


class FundaScraper(BaseScraper):
    """Scraper implementation for Funda property listing website."""

    def __init__(self, url: str) -> None:
        """Initialize the Funda scraper.

        Args:
            url: The URL of the Funda property listing to scrape

        Raises:
            ValueError: If the URL is not valid
        """
        super().__init__(url)
        self.soup = self.get_soup()
        self.feature_table: dict = self._parse_feature_table()

    def _find_script_tag(self) -> Dict[str, Any]:
        """Extract and parse the JSON-LD script tag containing property metadata.

        Returns:
            Dict containing the parsed JSON-LD data

        Raises:
            ValueError: If the script tag is not found or contains invalid JSON
        """
        script_tag = self.soup.find("script", type="application/ld+json")
        if not script_tag:
            raise ValueError("Could not find JSON-LD script tag")

        try:
            return json.loads(script_tag.string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON-LD data: {str(e)}")

    def _get_province(self) -> Optional[str]:
        """Extract the province (addressRegion) from the JSON-LD data.

        Returns:
            The province name if found, None otherwise
        """
        try:
            data = self._find_script_tag()
            return data.get("address", {}).get("addressRegion")
        except ValueError as e:
            print(f"Warning: Could not extract province: {str(e)}")
            return None

    def _extract_number_from_text(self, text: str) -> Optional[int]:
        """Extract the first number from a text string.

        Args:
            text: Text containing a number

        Returns:
            The first number found in the text, or None if no number is found
        """
        if not text:
            return None
        match = re.search(r"\d+", text)
        return int(match.group()) if match else None

    def _extract_area_from_text(self, text: str) -> Optional[int]:
        """Extract square meter value from text.

        Args:
            text: Text containing square meter value (e.g., "83 m²")

        Returns:
            The square meter value as an integer, or None if not found
        """
        if not text:
            return None
        match = re.search(r"(\d+)\s*m²", text)
        return int(match.group(1)) if match else None

    def _parse_feature_table(self) -> dict:
        """Parse feature table and extract key-value pairs.

        Returns:
            A dictionary where keys are the text within <dt> tags and values are the text within the <dd> tags right after.
        """
        feature_dict = {}
        try:
            # Find all <h3> tags
            for h3 in self.soup.find_all("h3"):
                # Get the definition list following the <h3>
                dl = h3.find_next("dl")
                if not dl:
                    continue

                # Iterate over each dt/dd pair
                for dt in dl.find_all("dt"):
                    dd = dt.find_next("dd")
                    key = dt.text.strip()
                    if dd:
                        value = dd.text.strip()
                        span = dd.find("span")
                        if span:
                            feature_dict[key] = span.text.strip()
                        else:
                            feature_dict[key] = value

        except Exception as e:
            print(f"Warning: Failed to parse feature: {str(e)}")

        return feature_dict

    def parse_property_address(self):
        """Parse the complete property address from the page title and JSON-LD data.

        Returns:
            Address object containing all available address components,
            or None if parsing fails
        """
        if not self.soup or not self.soup.title:
            return None

        try:
            address = parse_address_line(self.soup.title.string)
            address.province = self._get_province()
            return address
        except ValueError as e:
            print(f"Warning: Failed to parse address: {str(e)}")

    def parse_property_price(self) -> Optional[float]:
        """Parse the property price from the JSON-LD data.

        Returns:
            The property price as a float if available, None otherwise
        """
        try:
            data = self._find_script_tag()
            price = data.get("offers", {}).get("price")
            return float(price) if price is not None else None
        except (ValueError, TypeError) as e:
            print(f"Warning: Failed to parse price: {str(e)}")
            return None

    def close(self) -> None:
        """Clean up resources by closing the request handler."""
        if hasattr(self, "request_handler"):
            self.request_handler.close()
