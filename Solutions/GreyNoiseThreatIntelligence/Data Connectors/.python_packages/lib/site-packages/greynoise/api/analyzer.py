"""Analyzer module."""

import functools

import more_itertools


class Analyzer(object):
    """Aggregate stats related to IP addreses from a given text.

    :param api: API client
    :type api: greynoise.api.GreyNoise

    """

    ANALYZE_TEXT_CHUNK_SIZE = 10000

    SECTION_KEY_TO_ELEMENT_KEY = {
        "actors": "actor",
        "asns": "asn",
        "categories": "category",
        "classifications": "classification",
        "countries": "country",
        "operating_systems": "operating_system",
        "organizations": "organization",
        "tags": "tag",
        "spoofable": "spoofable",
        "source_countries": "country",
        "destination_countries": "country",
    }

    def __init__(self, api):
        self.api = api

    def analyze(self, text):
        """Aggregate stats related to IP addresses from a given text.

        :param text: Text input
        :type text: file-like | str
        :return: Aggregated stats for all the IP addresses found.
        :rtype: dict

        """
        if isinstance(text, str):
            text = text.splitlines(True)
        chunks = more_itertools.chunked(text, self.ANALYZE_TEXT_CHUNK_SIZE)
        text_stats = {
            "query": [],
            "count": 0,
            "stats": {},
        }
        text_ip_addresses = set()
        chunks_stats = [
            self._analyze_chunk(chunk, text_ip_addresses) for chunk in chunks
        ]
        functools.reduce(self._aggregate_stats, chunks_stats, text_stats)

        # This maps section dictionaries to list of dictionaries
        # (undoing mapping done previously to keep track of count values)
        for section_key, section_value in text_stats["stats"].items():
            section_element_key = self.SECTION_KEY_TO_ELEMENT_KEY[section_key]
            text_stats["stats"][section_key] = sorted(
                [
                    {section_element_key: element_key, "count": element_count}
                    for element_key, element_count in section_value.items()
                ],
                key=lambda element: (-element["count"], element[section_element_key]),
            )

        if text_ip_addresses:
            noise_ip_addresses = []
            riot_ip_addresses = []

            for result in self.api.quick(text_ip_addresses):
                if result["noise"]:
                    noise_ip_addresses.append(result["ip"])
                if result["riot"]:
                    riot_ip_addresses.append(result["ip"])

        else:
            noise_ip_addresses = set()
            riot_ip_addresses = set()

        ip_count = len(text_ip_addresses)
        noise_ip_count = len(noise_ip_addresses)
        riot_ip_count = len(riot_ip_addresses)
        not_noise_ip_count = ip_count - noise_ip_count - riot_ip_count
        if ip_count > 0:
            noise_ip_ratio = float(noise_ip_count) / ip_count
            riot_ip_ratio = float(riot_ip_count) / ip_count
        else:
            noise_ip_ratio = 0
            riot_ip_ratio = 0

        text_stats["summary"] = {
            "ip_count": ip_count,
            "noise_ip_count": noise_ip_count,
            "not_noise_ip_count": not_noise_ip_count,
            "riot_ip_count": riot_ip_count,
            "noise_ip_ratio": noise_ip_ratio,
            "riot_ip_ratio": riot_ip_ratio,
        }

        return text_stats

    def _analyze_chunk(self, text, text_ip_addresses):
        """Analyze chunk of lines that contain IP addresses from a given text.

        :param text: Text input
        :type text: str
        :param text_ip_addresses: IP addresses already seen in other chunks.
        :type text_ip_addresses: set(str)
        :return: Iterator with stats for each one of the IP addresses found.
        :rtype: dict

        """
        chunk_ip_addresses = set()
        for input_line in text:
            chunk_ip_addresses.update(self.api.IPV4_REGEX.findall(input_line))

        # Keep only IP addresses not seen in other chunks and query those
        chunk_ip_addresses -= text_ip_addresses
        text_ip_addresses.update(chunk_ip_addresses)

        chunk_stats = [
            self.api.stats(query=ip_address) for ip_address in chunk_ip_addresses
        ]
        return chunk_stats

    def _aggregate_stats(self, accumulator, chunk_stats):
        """Aggregate stats for different IP addresses.

        :param accumulator: Aggregated stats for multiple IP addresses.
        :type accumulator: dict
        :param chunk_stats:
            Stats for given chunk of text. These stats are not aggregated yet,
            so they are a list of stats for each query made for that chunk.
        :type chunk_stats: list(dict)

        """
        for query_stats in chunk_stats:
            accumulator["query"].append(query_stats["query"])
            accumulator["count"] += query_stats["count"]
            for section_key, section_values in query_stats["stats"].items():
                if section_values is None:
                    continue
                section_stats = accumulator["stats"].setdefault(section_key, {})

                # This maps a list of dictionaries to a dictionary
                # to easily keep track of counts.
                section_element_key = self.SECTION_KEY_TO_ELEMENT_KEY[section_key]
                for section_value in section_values:
                    element_key = section_value[section_element_key]
                    element_count = section_value["count"]
                    section_stats.setdefault(element_key, 0)
                    section_stats[element_key] += element_count

        return accumulator
