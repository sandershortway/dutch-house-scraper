"""Module for scraping Funda property listing website."""

import json
import re
from typing import Dict, List, Optional

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

    def _find_script_tag(self) -> List[Dict]:
        """Extract and parse the JSON-LD script tags containing property metadata.

        Returns:
            List containing the merged JSON-LD data from all script tags.

        Raises:
            ValueError: If no script tags are found or if they contain invalid JSON
        """
        script_tags = self.soup.find_all("script", type="application/ld+json")
        if not script_tags:
            raise ValueError("Could not find JSON-LD script tags")

        try:
            metadata = [json.loads(tag.string) for tag in script_tags]
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON-LD data: {str(e)}")

        return metadata

    def _get_neighbourhood(self) -> Optional[str]:
        """Extract the neighbourhood from the JSON-LD data.

        Returns:
            The province name if found, None otherwise
        """
        try:
            metadata = self._find_script_tag()

            # Check each metadata dictionary for the province information
            for data in metadata:
                if "itemListElement" in data:
                    item_list = data["itemListElement"]
                    return item_list[2]["item"]["name"]
            return None
        except ValueError as e:
            print(f"Warning: Could not extract province: {str(e)}")
            return None

    def _get_province(self) -> Optional[str]:
        """Extract the province (addressRegion) from the JSON-LD data.

        Returns:
            The province name if found, None otherwise
        """
        try:
            metadata = self._find_script_tag()
            # Check each metadata dictionary for the province information
            for data in metadata:
                if "address" in data and data["address"].get("addressRegion"):
                    return data["address"]["addressRegion"]
            return None
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

    def parse_listing_date(self) -> Optional[str]:
        """Extract the listing date from the JSON data in the script tag.

        Returns:
            The listing date as a string if found, None otherwise
        """
        try:
            # Find the script tag containing the __NUXT_DATA__
            script_tag = self.soup.find("script", {"id": "__NUXT_DATA__"})
            if not script_tag:
                return None

            # Parse the JSON data
            data = json.loads(script_tag.string)

            # Convert data to a flat list to make it easier to search
            flat_data = []
            for item in data:
                if isinstance(item, (list, dict)):
                    flat_data.extend(str(x) for x in item)
                else:
                    flat_data.append(str(item))

            # Find the index of the target string
            try:
                target_index = flat_data.index("overdracht-aangeboden-sinds")
                # The listing date should be 2 positions after our target
                if target_index + 2 < len(flat_data):
                    return flat_data[target_index + 2]
            except ValueError:
                return None

            return None
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Warning: Failed to parse listing date: {str(e)}")
            return None

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
            address.neighbourhood = self._get_neighbourhood()
            return address
        except ValueError as e:
            print(f"Warning: Failed to parse address: {str(e)}")

    def parse_property_price(self) -> Optional[float]:
        """Parse the property price from the JSON-LD data.

        Returns:
            The property price as a float if available, None otherwise
        """
        try:
            metadata = self._find_script_tag()

            for data in metadata:
                if "offers" in data and data["offers"].get("price"):
                    price = data["offers"]["price"]
            return float(price) if price is not None else None
        except (ValueError, TypeError) as e:
            print(f"Warning: Failed to parse price: {str(e)}")
            return None

    def close(self) -> None:
        """Clean up resources by closing the request handler."""
        if hasattr(self, "request_handler"):
            self.request_handler.close()
