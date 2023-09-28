import re

import stix2patterns.inspector

HASHES_REGEX = {
    "MD5": (r"^[a-fA-F0-9]{32}$", "MD5"),
    "MD6": (r"^[a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{56}|\
    [a-fA-F0-9]{64}|[a-fA-F0-9]{96}|[a-fA-F0-9]{128}$", "MD6"),
    "RIPEMD160": (r"^[a-fA-F0-9]{40}$", "RIPEMD-160"),
    "SHA1": (r"^[a-fA-F0-9]{40}$", "SHA-1"),
    "SHA224": (r"^[a-fA-F0-9]{56}$", "SHA-224"),
    "SHA256": (r"^[a-fA-F0-9]{64}$", "SHA-256"),
    "SHA384": (r"^[a-fA-F0-9]{96}$", "SHA-384"),
    "SHA512": (r"^[a-fA-F0-9]{128}$", "SHA-512"),
    "SHA3224": (r"^[a-fA-F0-9]{56}$", "SHA3-224"),
    "SHA3256": (r"^[a-fA-F0-9]{64}$", "SHA3-256"),
    "SHA3384": (r"^[a-fA-F0-9]{96}$", "SHA3-384"),
    "SHA3512": (r"^[a-fA-F0-9]{128}$", "SHA3-512"),
    "SSDEEP": (r"^[a-zA-Z0-9/+:.]{1,128}$", "SSDEEP"),
    "WHIRLPOOL": (r"^[a-fA-F0-9]{128}$", "WHIRLPOOL"),
}


def verify_object(patt_data):
    error_list = []
    msg = "FAIL: '{}' is not a valid {} hash"

    # iterate over observed objects
    for type_name, comp in patt_data.comparisons.items():
        for obj_path, op, value in comp:
            if 'hashes' in obj_path:
                hash_selector = obj_path[-1]
                if hash_selector is not stix2patterns.inspector.INDEX_STAR:
                    hash_type = \
                        hash_selector.upper().replace('-', '').replace("'", "")
                    hash_string = value.replace("'", "")
                    if hash_type in HASHES_REGEX:
                        if not re.match(HASHES_REGEX[hash_type][0], hash_string):
                            error_list.append(
                                msg.format(hash_string, hash_selector)
                            )
    return error_list
