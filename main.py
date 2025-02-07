"""Main script to test the Funda web scraper."""

from scrapers.funda import FundaScraper


def main():
    """Run the Funda scraper on a test URL."""
    url = "https://www.funda.nl/detail/koop/leiden/huis-vondellaan-26/43889182/"

    try:
        # Initialize and run the scraper
        scraper = FundaScraper(url)

        print(scraper._parse_kenmerken_table())

        # Get address and price for completeness
        address = scraper.parse_property_address()
        price = scraper.parse_property_price()

        if address:
            print(f"\nAddress: {address}")
        if price:
            print(f"Price: {price}")

        # Clean up
        scraper.close()

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
