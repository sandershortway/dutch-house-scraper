"""Main script to test the Funda web scraper."""

import json
import random
import time
from pathlib import Path
from typing import List

from scrapers.funda import FundaScraper


class RequestManager:
    def __init__(self, json_file_path: str):
        """Initialize the RequestManager with a path to a JSON file containing URLs.

        Args:
            json_file_path (str): Path to the JSON file containing listing URLs
        """
        self.json_file_path = Path(json_file_path)
        self.urls: List[str] = []
        self.load_requests()

    def load_requests(self) -> None:
        """Load URLs from the JSON file."""
        if not self.json_file_path.exists():
            raise FileNotFoundError(f"Request file not found: {self.json_file_path}")

        with open(self.json_file_path, "r") as f:
            data = json.load(f)

        if not isinstance(data, dict) or "urls" not in data:
            raise ValueError("JSON file must contain a 'urls' key with a list of URLs")

        self.urls = data["urls"]

    def get_urls(self) -> List[str]:
        """Get the list of URLs to scrape.

        Returns:
            List[str]: List of URLs
        """
        return self.urls

    def add_url(self, url: str) -> None:
        """Add a new URL to the list and save to file.

        Args:
            url (str): URL to add
        """
        if url not in self.urls:
            self.urls.append(url)
            self._save_to_file()

    def remove_url(self, url: str) -> None:
        """Remove a URL from the list and save to file.

        Args:
            url (str): URL to remove
        """
        if url in self.urls:
            self.urls.remove(url)
            self._save_to_file()

    def _save_to_file(self) -> None:
        """Save the current URLs back to the JSON file."""
        data = {"urls": self.urls}
        with open(self.json_file_path, "w") as f:
            json.dump(data, f, indent=4)


def main():
    """Run the Funda scraper on URLs from the request file."""
    request_manager = RequestManager("example_requests.json")

    for url in request_manager.get_urls():
        print(f"\nProcessing: {url}")
        try:
            # Initialize the scraper for each URL
            scraper = FundaScraper(url)

            # Scrape the data
            listing = scraper.get_listing()
            # address = scraper.parse_property_address()
            # price = scraper.parse_property_price()
            feature_table = scraper._parse_feature_table()
            # listing_date = scraper.parse_listing_date()

            # Print the results
            if listing.address:
                print(f"Address: {listing.address}")
            if listing.price:
                print(f"Price: {listing.price}")
            # if listing_date:
            #     print(f"Listed since: {listing_date}")
            if feature_table:
                print("Features:")
                for key, value in feature_table.items():
                    print(f"{key}: {value}")

            # Clean up
            scraper.close()

            # Sleep a random amount of time to avoid overwhelming the server
            sleep_time = random.uniform(1, 5)
            print(f"Sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            continue


if __name__ == "__main__":
    main()
