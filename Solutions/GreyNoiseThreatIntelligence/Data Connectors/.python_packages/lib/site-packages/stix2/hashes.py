"""
Library support for hash algorithms, independent of STIX specs.
"""

import enum
import re


class Hash(enum.Enum):
    """
    Instances represent a hash algorithm, independent of STIX spec version.
    Different spec versions may have different requirements for naming; this
    allows us to refer to and use hash algorithms in a spec-agnostic way.
    """
    MD5 = 0
    MD6 = 1
    RIPEMD160 = 2
    SHA1 = 3
    SHA224 = 4
    SHA256 = 5
    SHA384 = 6
    SHA512 = 7
    SHA3224 = 8
    SHA3256 = 9
    SHA3384 = 10
    SHA3512 = 11
    SSDEEP = 12
    WHIRLPOOL = 13
    TLSH = 14


# Regexes used to sanity check hash values.  Could also be combined with the
# enum values themselves using enum definition tricks, but... this seems
# simpler.
_HASH_REGEXES = {
    Hash.MD5: r"^[a-f0-9]{32}$",
    Hash.MD6: r"^[a-f0-9]{32}|[a-f0-9]{40}|[a-f0-9]{56}|[a-f0-9]{64}|[a-f0-9]{96}|[a-f0-9]{128}$",
    Hash.RIPEMD160: r"^[a-f0-9]{40}$",
    Hash.SHA1: r"^[a-f0-9]{40}$",
    Hash.SHA224: r"^[a-f0-9]{56}$",
    Hash.SHA256: r"^[a-f0-9]{64}$",
    Hash.SHA384: r"^[a-f0-9]{96}$",
    Hash.SHA512: r"^[a-f0-9]{128}$",
    Hash.SHA3224: r"^[a-f0-9]{56}$",
    Hash.SHA3256: r"^[a-f0-9]{64}$",
    Hash.SHA3384: r"^[a-f0-9]{96}$",
    Hash.SHA3512: r"^[a-f0-9]{128}$",
    Hash.SSDEEP: r"^[a-z0-9/+:.]{1,128}$",
    Hash.WHIRLPOOL: r"^[a-f0-9]{128}$",
    Hash.TLSH: r"^[a-f0-9]{70}$",
}


# compile all the regexes; be case-insensitive
for hash_, re_str in _HASH_REGEXES.items():
    _HASH_REGEXES[hash_] = re.compile(re_str, re.I)


def infer_hash_algorithm(name):
    """
    Given a hash algorithm name, try to figure out which hash algorithm it
    refers to.  This primarily enables some user flexibility in naming hash
    algorithms when creating STIX content.

    :param name: A hash algorithm name
    :return: A Hash enum value if the name was recognized, or None if it was
        not recognized.
    """
    enum_name = name.replace("-", "").upper()

    try:
        enum_obj = Hash[enum_name]
    except KeyError:
        enum_obj = None

    return enum_obj


def check_hash(hash_, value):
    """
    Sanity check the given hash value, against the given hash algorithm.

    :param hash_: The hash algorithm, as one of the Hash enums
    :param value: A hash value as string
    :return: True if the value seems okay; False if not
    """

    # I guess there's no need to require a regex mapping for the algorithm...
    # Just assume it's okay if we have no way to check it.
    result = True
    regex = _HASH_REGEXES.get(hash_)
    if regex:
        result = bool(regex.match(value))

    return result
