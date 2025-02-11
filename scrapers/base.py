from abc import ABC, abstractmethod
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from models import Address, Listing, Price, Property, Website
from utils.request_handler import RequestHandler
from utils.utils import is_valid_url


class BaseScraper(ABC):
    def __init__(self, url: str):
        self.request_handler = RequestHandler()

        if is_valid_url(url):
            self.url: str = url
        else:
            raise ValueError(f"Invalid url: '{url}'")

        self.website: Website = self._get_website()

    def _get_website(self) -> Website:
        """Get website from url."""
        if "funda" in self.url:
            return Website.FUNDA
        if "huislijn" in self.url:
            return Website.HUISLIJN
        raise ValueError(f"Unknown website encountered in url: {self.url}")

    def _get_safe_filename(self) -> str:
        """Generate a safe filename from the URL.

        Returns:
            A filename-safe string based on the URL path
        """
        parsed = urlparse(self.url)
        # Remove common prefixes and use the path
        path = parsed.path.strip("/").replace("/", "_")
        return f"{parsed.netloc}_{path}.html"

    def get_html(self):
        """Get HTML content from a URL using the request handler and save to file.

        Returns:
            str: The HTML content of the page

        Side effects:
            Saves the HTML content to a file in the 'cached_pages' directory
        """
        html_data = self.request_handler.get(self.url)

        # Create cache directory if it doesn't exist
        cache_dir = Path("cached_pages")
        cache_dir.mkdir(exist_ok=True)

        # Generate safe filename and save HTML
        filename = self._get_safe_filename()
        cache_path = cache_dir / filename

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(html_data)
            print(f"Saved HTML to: {cache_path}")
        except Exception as e:
            print(f"Warning: Failed to save HTML file: {str(e)}")

        return html_data

    def get_soup(self):
        html = self.get_html()
        return BeautifulSoup(html, "html.parser")

    def __del__(self):
        """Cleanup the request handler when the scraper is destroyed"""
        if hasattr(self, "request_handler"):
            self.request_handler.close()

    @abstractmethod
    def get_property_address(self) -> Address:
        pass

    @abstractmethod
    def get_property_price(self) -> Price:
        pass

    @abstractmethod
    def get_property_information(self) -> Property:
        pass

    def get_listing(self) -> Listing:
        return Listing(
            self.get_property_address(),
            self.get_property_information(),
            self.get_property_price(),
            self.website,
            self.url,
        )
