from enum import Enum

# Mapping of aliases for listing statuses
_listing_status_aliases = {
    "Beschikbaar": ["beschikbaar", "available"],
    "Onder bod": ["onder bod", "under offer"],
    "Verkocht": ["verkocht", "sold", "verkocht onder voorbehoud"],
}


class ListingStatus(Enum):
    BESCHIKBAAR: str = "Beschikbaar"
    ONDER_BOD: str = "Onder bod"
    VERKOCHT: str = "Verkocht"

    @classmethod
    def from_string(cls, text: str) -> "ListingStatus":
        """Get the ListingStatus enum value from a string, checking against known aliases.

        Args:
            text: The string to convert to a ListingStatus

        Returns:
            The matching ListingStatus enum value

        Raises:
            ValueError: If no matching status is found
        """
        if not text:
            raise ValueError("Cannot determine listing status from empty string")

        text = text.lower().strip()

        for enum_member in cls:
            aliases = _listing_status_aliases[enum_member.value]
            if (
                text in [alias.lower() for alias in aliases]
                or text == enum_member.value.lower()
            ):
                return enum_member

        raise ValueError(f"No matching listing status found for: '{text}'")
