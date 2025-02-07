"""
This module provides a robust HTTP request handling functionality with built-in retry mechanisms
and proper header management for web scraping purposes.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RequestHandler:
    """A class that handles HTTP requests with built-in retry logic and proper header management.

    This class provides a robust way to make HTTP requests while handling common issues like
    temporary failures and rate limiting through automatic retries. It maintains a persistent
    session and uses standard browser-like headers to avoid detection.
    """

    def __init__(self):
        """Initialize the RequestHandler with a configured session and default headers.

        Sets up a requests session with retry logic and configures default headers
        that mimic a standard web browser.
        """
        self.session = self._create_session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
        }

    def _create_session(self):
        """Create a session with retry logic.

        Configures a requests session with a retry policy that handles temporary failures
        and rate limiting. It also sets up standard browser-like headers.

        Returns:
            requests.Session: A configured session with retry logic.
        """
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
        }
        session.headers.update(headers)

        retry_policy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[408, 429, 500, 502, 503, 504, 520],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_policy)
        session.mount("https://", adapter)
        return session

    def get(self, url):
        """Make a GET request to the specified URL.

        Args:
            url (str): The URL to send the GET request to.

        Returns:
            str: The text content of the response.

        Raises:
            requests.exceptions.RequestException: If the request fails after retries.
        """
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text

    def close(self):
        """Close the current session and clean up resources.

        Should be called when the RequestHandler is no longer needed to ensure
        proper cleanup of network resources.
        """
        self.session.close()
