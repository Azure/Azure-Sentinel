
#!/usr/bin/env python3
#
# Copyright (C) SlashNext, Inc. (www.slashnext.com)
#
# License:     Subject to the terms and conditions of SlashNext EULA, SlashNext grants to Customer a non-transferable,
#              non-sublicensable, non-exclusive license to use the Software as expressly permitted in accordance with
#              Documentation or other specifications published by SlashNext. The Software is solely for Customer"s
#              internal business purposes. All other rights in the Software are expressly reserved by SlashNext.
#



import azure.functions as func
import hashlib
import json
import logging
import re

URL_REGEX_PATTERN = r"(?:(?:https?|ftp|hxxps?):\/\/|www\[?\.\]?|ftp\[?\.\]?)(?:(?:[-A-Z0-9_@:%]+?\[?\.\]?)+" \
                    r"[-A-Z0-9]+|(?:[-A-Z0-9_:%]+?@0x[A-Z0-9]{8}))(?::[0-9]+)?\.?(?:(?:\/?|\?)[-A-Z0-9+&@#\/" \
                    r"%=~_$?!:,*'\|\[\].\(\);\^\{\}]*[A-Z0-9+&@#\/%=~_$(*\-\?\|!:\[\]\{\}])?"

def extract_urls_json(data):
    """
    Extracts URLs from raw data of log analytics.
    :param data: Raw data of log analytics. (dict)
    :return: List of URLs. (list)
    """
    list_of_urls = []
    url_pattern_regex = re.compile(URL_REGEX_PATTERN, re.IGNORECASE)
    if 'tables' in data:
        if 'rows' in data['tables'][0]:
            for s_row in (data['tables'][0]['rows']):
                for s_col in s_row:
                    if isinstance(s_col, str):
                        data = url_pattern_regex.findall(s_col)
                        if data:
                            list_of_urls.extend(data)
    return list_of_urls


def split_list(data, size=10000):
    """
    Split list in smaller chunks.
    :param data: List of string. (list)
    :param size: Size of list chunk. (int)
    :return: List of lists. (list)
    """
    sub_lists = []
    for i in range(0, len(data), size):
        sub_lists.append(data[i:i + size])
    return sub_lists


def md5_mapping(data):
    """
    Generates list of dictionary containg md5 and url.
    :param data: List of URLs. (list)
    :return: List of dictionary. (list)
    """
    mapping = []
    for s_url in data:
        md5_hash = hashlib.md5(s_url.encode('utf-8')).hexdigest()
        mapping.append({'hash': f'{md5_hash}', 'url': f'{s_url}'})
    return mapping


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        label = req.params.get('label')
        if label is None:
            return func.HttpResponse("Valid query param 'label' is missing", status_code=500)
        logging.info("param check passed")
        req_body = req.get_json()
        logging.info(str(label))
        logging.info(str(req_body))
        if label == 'extract':
            filtered_data = extract_urls_json(req_body)
            result = split_list(filtered_data, 5000)
        elif label == 'mapping':
            result = md5_mapping(req_body)
        return func.HttpResponse(json.dumps(result), status_code=200)
    except Exception as err:
        logging.error(f"Error: {err}")
        return func.HttpResponse(str(err), status_code=500)
