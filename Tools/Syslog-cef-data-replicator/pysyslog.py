#!/usr/bin/env python

from __future__ import print_function

import logging
import re

# Setup logging null handler
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def parse(str_input):
    """
    Parse a string in CEF format and return a dict with the header values
    and the extension data.
    """
    values = dict()


    is_starts_with_PRI = re.search("^\<[0-9]+\>", str_input[:10])
    if is_starts_with_PRI:
        header_re = r'^\<([0-9]+)\>\s{0,1}(.*)'
        res = re.search(header_re, str_input)
        values["pri"] = res.group(1)
        str_input = res.group(2)

    contains_syslog_version = re.search("^(\d{1})\s(.*)", str_input[:2])

    if contains_syslog_version:
        header_re = r'^(\d{1})\s(.*)'
        res = re.search(header_re, str_input)
        values["version"] = res.group(1)
        str_input = res.group(2)

    contains_datetime_format1 = re.search("^(\w{1,3}\s\d{1,2}\s\d{1,4}[\sT]\d{1,2}\:\d{1,2}\:\d{1,2})",str_input)
    contains_datetime_format2 = re.search("^(\d{2}(?:\d{2})?-\d{1,2}-\d{1,2}[\sT]\d{1,2}\:\d{1,2}\:\d{1,2})",str_input)
    contains_datetime_format3 = re.search("^(\d{9,13}[\.][\d]{0,10})\s(.*)",str_input)
    contains_datetime_format4 = re.search("^(\w{1,3}\s\d{1,2}[\sT]\d{1,2}\:\d{1,2}\:\d{1,2})",str_input)

    # Mar 20 2022 10:00:00
    if contains_datetime_format1:
        header_re = r'^(\w{1,3}\s\d{1,2}\s\d{1,4}[\sT]\d{1,2}:\d{1,2}:\d{1,2}(?:\.\d{1,10})?)\s(.*)'
        res = re.search(header_re, str_input)
        values["ISOTimeStamp"] = res.group(1)
        str_input = res.group(2)
    # 2022-03-20T10:00:00
    elif contains_datetime_format2:
        header_re = r'^(\d{2}(?:\d{2})?-\d{1,2}-\d{1,2}[\sT]\d{1,2}:\d{1,2}:\d{1,2}(?:\.\d{1,10})?Z?)\s(.*)'
        res = re.search(header_re, str_input)
        values["ISOTimeStamp"] = res.group(1)
        str_input = res.group(2)
    elif contains_datetime_format3:
        header_re = r'^(\d{9,13}[\.][\d]{0,10})\s(.*)'
        res = re.search(header_re, str_input)
        values["ISOTimeStamp"] = res.group(1)
        str_input = res.group(2)
    elif contains_datetime_format4:
        header_re = r'^(\w{1,3}\s\d{1,2}[\sT]\d{1,2}:\d{1,2}:\d{1,2}(?:\.\d{1,10})?)\s(.*)'
        res = re.search(header_re, str_input)
        values["ISOTimeStamp"] = res.group(1)
        str_input = res.group(2)

    contains_hostname = re.search("^([\.\w\-]+)\s(.*)",str_input)

    if contains_hostname:
        header_re = r'^([\.\w\-]+)\s(.*)'
        res = re.search(header_re, str_input)
        values["hostName"] = res.group(1)
        values["restofmessage"] = res.group(2)

    

    # Now we're done!
    logger.debug('Returning values: ' + str(values))
    return values


if __name__ == "__main__":

    import sys
    import json

    if len(sys.argv) != 2:
        print("USAGE: %s <file>" % sys.argv[0])
        sys.exit(-1)

    file = sys.argv[1]
    with open(file, "r") as f:
        for line in f.readlines():
            line = line.rstrip('\n')

            # Read the file, and parse each line of CEF into a separate JSON
            # document to stdout
            try:
                values = parse(line)
            except (TypeError, ValueError) as e:
                sys.stderr.write('{0} parsing line:\n{1}\n'.format(e.message, line))
            else:
                if values:
                    print(json.dumps(values))
                if not values:
                    print('No output returned, maybe your regex did not match?')