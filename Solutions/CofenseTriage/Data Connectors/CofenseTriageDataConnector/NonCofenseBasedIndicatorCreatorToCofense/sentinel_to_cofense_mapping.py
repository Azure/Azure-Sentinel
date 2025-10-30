"""This file contains function for mapping of sentinel and cofense indicators."""
from ..SharedCode.consts import COFENSE_SOURCE_PREFIX


class SentinelToCofenseMapping:
    """To map field values of Sentinel and cofense indicators."""

    def get_threat_value(self, pattern):
        """To convert sentinel indicator pattern to threat value."""
        if pattern is not None:
            return (pattern.split("=")[1]).strip("' ]")
        else:
            return None

    def get_indicator_source(self, sentinel_indicator_source):
        """To get the sentinel indicator source."""
        # To do: convert split function to startswith function for checking prefix.
        if (
            sentinel_indicator_source is not None
            and sentinel_indicator_source.split(":")[0].lower().strip()
            != COFENSE_SOURCE_PREFIX.split(":")[0].lower().strip()
        ):
            return sentinel_indicator_source
        else:
            return None

    # To do: remove unnecessary else condition.
    def get_cofense_threat_type(self, indicators):
        """To convert sentinel indicator type to cofense accepted indicator type."""
        # getting indicator type.
        sentinel_indicator_pattern_type = indicators.get("properties", {}).get(
            "patternType", None
        )
        cofense_indicator_pattern_type = None
        # if indicator type is url in sentinel then URL in cofense.
        if sentinel_indicator_pattern_type == "url":
            cofense_indicator_pattern_type = "URL"

        # if indicator type is domain-name in sentinel then Hostname in cofense.
        elif sentinel_indicator_pattern_type == "domain-name":
            cofense_indicator_pattern_type = "Hostname"

        # if indicator type is file in sentinel then MD5 or SHA256 in cofense.
        elif sentinel_indicator_pattern_type == "file":
            sentinel_indicator_pattern = indicators.get("properties", {}).get(
                "pattern", None
            )
            if sentinel_indicator_pattern is not None:
                sentinel_file_pattern = sentinel_indicator_pattern.split("'")[1]

                if sentinel_file_pattern == "MD5":
                    cofense_indicator_pattern_type = "MD5"
                elif sentinel_file_pattern == "SHA-256":
                    cofense_indicator_pattern_type = "SHA256"
                else:
                    cofense_indicator_pattern_type = None
            else:
                cofense_indicator_pattern_type = None
        else:
            cofense_indicator_pattern_type = None

        return cofense_indicator_pattern_type
