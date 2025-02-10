"""Main script to test the Funda web scraper."""

from scrapers.funda import FundaScraper


def main():
    """Run the Funda scraper on a test URL."""
    url = "https://www.funda.nl/en/detail/koop/leiden/huis-vondellaan-26/43889182/"

    try:
        # Initialize the scraper
        scraper = FundaScraper(url)

        address = scraper.parse_property_address()
        price = scraper.parse_property_price()
        feature_table = scraper._parse_feature_table()
        listing_date = scraper.parse_listing_date()

        if address:
            print(f"\nAddress: {address}")
        if price:
            print(f"\nPrice: €{price:,.2f}")
        if listing_date:
            print(f"\nListed since: {listing_date}")
        if feature_table:
            print("\nFeatures:")
            for key, value in feature_table.items():
                print(f"{key}: {value}")

        # Clean up
        scraper.close()
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
