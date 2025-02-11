"""Module for scraping Funda property listing website."""

import json
import re
from typing import Dict, List, Optional

from models.listing_status import ListingStatus
from models.scraper_models import Address, Price, Property
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
        self.feature_table: dict = self._get_feature_table()

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

    def get_listing_status(self) -> ListingStatus:
        try:
            feature_table = self._get_feature_table()

            # Try both house and apartment type fields
            status = feature_table.get("Status")

            if not status:
                raise ValueError("No status found in feature table")

            return ListingStatus.from_string(status)

        except (KeyError, ValueError, AttributeError) as e:
            print(f"Warning: Failed to parse status: {str(e)}")
            return None

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

    def _get_feature_table(self) -> dict:
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

    def get_property_address(self) -> Address:
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

    def get_property_price(self) -> Price:
        """Extract and parse price information from the JSON-LD data.

        This method retrieves various price-related details from the property listing,
        including the asking price and price per square meter. For sold properties,
        it will attempt to extract the sale price if available.

        Returns:
            Price: A Price object containing the parsed price information.
                  Fields may be None if data is missing or cannot be parsed.

        Note:
            - All prices are converted to float values
            - Prices are expected to be in EUR
            - Returns an empty Price object with None values if parsing fails
        """
        price_information = Price()

        try:
            metadata = self._find_script_tag()
            price = None
            living_area = None

            for data in metadata:
                # Extract asking price from offers
                if "offers" in data and isinstance(data["offers"], dict):
                    price = data["offers"].get("price")

            # Set asking price
            if price is not None:
                try:
                    price_information.asking_price = float(price)

                    # Calculate price per square meter if both price and area are available
                    if living_area and float(living_area) > 0:
                        price_information.asking_price_per_square_meter = (
                            price_information.asking_price / float(living_area)
                        )
                except (ValueError, TypeError):
                    print("Warning: Failed to convert price to float")

        except (KeyError, ValueError, TypeError, AttributeError) as e:
            print(f"Warning: Failed to parse price information: {str(e)}")
            return Price()  # Return empty Price object with None values

        return price_information

    def get_property_type(self) -> str:
        """Extract and parse the property type from the feature table.

        This method retrieves the property type from either the 'Soort woonhuis' or
        'Soort appartement' field in the feature table. For properties with multiple
        type descriptions (comma-separated), only the first type is returned.

        Returns:
            str: The property type (e.g., "Eengezinswoning", "Portiekflat").
                 Returns None if the type cannot be determined.

        Note:
            - Only returns the part before the comma if multiple types are present
            - Handles both house and apartment type fields
        """
        try:
            feature_table = self._get_feature_table()

            # Try both house and apartment type fields
            property_type = feature_table.get("Soort woonhuis") or feature_table.get(
                "Soort appartement"
            )

            # Ignore whatever is within the brackets
            property_type = re.sub(r"\(.*\)", "", property_type)

            if not property_type:
                raise ValueError("No property type found in feature table")

            # If there's a comma, only take the first part
            return property_type.split(",")[0].strip()

        except (KeyError, ValueError, AttributeError) as e:
            print(f"Warning: Failed to parse property type: {str(e)}")
            return None

    def get_property_information(self) -> Property:
        """Extract and parse property information from the feature table.

        This method retrieves key property details including energy label, living area,
        number of rooms, and build year from the Funda feature table. It handles
        potential missing or malformed data gracefully.

        Returns:
            Property: A Property object containing the parsed information.
                     Fields may be None if data is missing or cannot be parsed.

        Note:
            - Living area is converted from string (e.g., "100 m²") to integer
            - Build year and number of rooms are converted to integers
            - Energy label is kept as string (e.g., "A", "B+", etc.)
        """
        try:
            feature_table = self._get_feature_table()

            # Extract and clean living area (convert "120 m²" to 120)
            living_area_str = feature_table.get("Wonen", "0 m²")
            living_area = int(living_area_str.split()[0]) if living_area_str else None

            # Extract and convert number of rooms to integer
            num_rooms_str = feature_table.get("Aantal kamers", "0")
            num_rooms = int(num_rooms_str.split()[0]) if num_rooms_str else None

            # Extract and convert build year to integer
            build_year_str = feature_table.get("Bouwjaar")
            build_year = (
                int(build_year_str)
                if build_year_str and build_year_str.isdigit()
                else None
            )

            # Energy label is kept as string
            energylabel = feature_table.get("Energielabel")

            return Property(
                energylabel=energylabel,
                living_area=living_area,
                num_rooms=num_rooms,
                build_year=build_year,
                type=self.get_property_type(),
            )

        except (KeyError, ValueError, TypeError) as e:
            print(f"Warning: Failed to parse property information: {str(e)}")
            return Property()

    def close(self) -> None:
        """Clean up resources by closing the request handler."""
        if hasattr(self, "request_handler"):
            self.request_handler.close()
