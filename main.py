"""Main script to test the Funda web scraper."""

from scrapers.funda import FundaScraper
from utils.request_manager import RequestManager


def main():
    """Run the Funda scraper on URLs from the request file.

    This function processes each URL in the request file, scraping property
    information using the FundaScraper.
    """
    request_manager = RequestManager("example_requests.json")

    for url in request_manager.get_urls():
        print(f"\nProcessing: {url}")
        try:
            # Initialize the scraper and get listing information
            scraper = FundaScraper(url)
            listing = scraper.get_listing()

            # Print listing information
            print("\nListing Details:")
            if listing.address:
                print(f"Address: {listing.address.street} {listing.address.number}")
                print(f"Location: {listing.address.city} ({listing.address.zip_code})")
                if listing.address.neighbourhood:
                    print(f"Neighbourhood: {listing.address.neighbourhood}")

            if listing.price:
                print(f"Status: {listing.status.value}")
                if listing.price.asking_price:
                    print(f"Asking Price: €{listing.price.asking_price:,.2f}")
                if listing.price.asking_price_per_square_meter:
                    print(
                        f"Price per m²: €{listing.price.asking_price_per_square_meter:,.2f}"
                    )
                print(f"Listing date: {scraper.parse_listing_date()}")

            if listing.property:
                print("\nProperty Details:")
                if listing.property.type:
                    print(f"Type: {listing.property.type}")
                if listing.property.living_area:
                    print(f"Living Area: {listing.property.living_area} m²")
                if listing.property.num_rooms:
                    print(f"Number of Rooms: {listing.property.num_rooms}")
                if listing.property.build_year:
                    print(f"Build Year: {listing.property.build_year}")
                if listing.property.energylabel:
                    print(f"Energy Label: {listing.property.energylabel}")

            # Clean up resources
            scraper.close()

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            continue


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
