"""Main script to test the Funda web scraper."""

from scrapers.funda import FundaScraper


def main():
    """Run the Funda scraper on a test URL."""
    url = "https://www.funda.nl/en/detail/koop/leiden/huis-vondellaan-26/43889182/"

    try:
        # Initialize the scraper
        scraper = FundaScraper(url)

        # Parse data from the URL
        address = scraper.parse_property_address()
        price = scraper.parse_property_price()
        feature_table = scraper._parse_feature_table()

        if address:
            print(f"\nAddress: {address}")
        if price:
            print(f"Price: {price}")
        if feature_table:
            print(f"Other Features: {feature_table}")

        # Clean up
        scraper.close()

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
