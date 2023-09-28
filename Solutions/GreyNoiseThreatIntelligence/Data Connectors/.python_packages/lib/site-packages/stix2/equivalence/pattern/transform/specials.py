"""
Some simple comparison expression normalization functions.
"""
import socket

from stix2.equivalence.pattern.compare.comparison import (
    object_path_to_raw_values,
)

# Values we can use as wildcards in path patterns
_ANY_IDX = object()
_ANY_KEY = object()
_ANY = object()


def _path_is(object_path, path_pattern):
    """
    Compare an object path against a pattern.  This enables simple path
    recognition based on a pattern, which is slightly more flexible than exact
    equality: it supports some simple wildcards.

    The path pattern must be an iterable of values: strings for key path steps,
    ints or "*" for index path steps, or wildcards.  Exact matches are required
    for non-wildcards in the pattern.  For the wildcards, _ANY_IDX matches any
    index path step; _ANY_KEY matches any key path step, and _ANY matches any
    path step.

    Args:
        object_path: An ObjectPath instance
        path_pattern: An iterable giving the pattern path steps

    Returns:
        True if the path matches the pattern; False if not
    """
    path_values = object_path_to_raw_values(object_path)

    path_iter = iter(path_values)
    patt_iter = iter(path_pattern)

    result = True
    while True:
        path_val = next(path_iter, None)
        patt_val = next(patt_iter, None)

        if path_val is None and patt_val is None:
            # equal length sequences; no differences found
            break

        elif path_val is None or patt_val is None:
            # unequal length sequences
            result = False
            break

        elif patt_val is _ANY_IDX:
            if not isinstance(path_val, int) and path_val != "*":
                result = False
                break

        elif patt_val is _ANY_KEY:
            if not isinstance(path_val, str):
                result = False
                break

        elif patt_val is not _ANY and patt_val != path_val:
            result = False
            break

    return result


def _mask_bytes(ip_bytes, prefix_size):
    """
    Retain the high-order 'prefix_size' bits from ip_bytes, and zero out the
    remaining low-order bits.  This side-effects ip_bytes.

    Args:
        ip_bytes: A mutable byte sequence (e.g. a bytearray)
        prefix_size: An integer prefix size
    """
    addr_size_bytes = len(ip_bytes)
    addr_size_bits = 8 * addr_size_bytes

    assert 0 <= prefix_size <= addr_size_bits

    num_fixed_bytes = prefix_size // 8
    num_zero_bytes = (addr_size_bits - prefix_size) // 8

    if num_zero_bytes > 0:
        ip_bytes[addr_size_bytes - num_zero_bytes:] = b"\x00" * num_zero_bytes

    if num_fixed_bytes + num_zero_bytes != addr_size_bytes:
        # The address boundary doesn't fall on a byte boundary.
        # So we have a byte for which we have to zero out some
        # bits.
        num_1_bits = prefix_size % 8
        mask = ((1 << num_1_bits) - 1) << (8 - num_1_bits)
        ip_bytes[num_fixed_bytes] &= mask


def windows_reg_key(comp_expr):
    """
    Lower-cases the rhs, depending on the windows-registry-key property
    being compared.  This enables case-insensitive comparisons between two
    patterns, for those values.  This side-effects the given AST.

    Args:
        comp_expr: A _ComparisonExpression object whose type is
            windows-registry-key
    """
    if _path_is(comp_expr.lhs, ("key",)) \
            or _path_is(comp_expr.lhs, ("values", _ANY_IDX, "name")):
        comp_expr.rhs.value = comp_expr.rhs.value.lower()


def ipv4_addr(comp_expr):
    """
    Canonicalizes a CIDR IPv4 address by zeroing out low-order bits, according
    to the prefix size.  This affects the rhs when the "value" property of an
    ipv4-addr is being compared.  If the prefix size is 32, the size suffix is
    simply dropped since it's redundant.  If the value is not a valid CIDR
    address, then no change is made.  This also runs the address through the
    platform's IPv4 address processing functions (inet_aton() and inet_ntoa()),
    which can adjust the format.

    This side-effects the given AST.

    Args:
        comp_expr: A _ComparisonExpression object whose type is ipv4-addr.
    """
    if _path_is(comp_expr.lhs, ("value",)):
        value = comp_expr.rhs.value
        slash_idx = value.find("/")
        is_cidr = slash_idx >= 0

        if is_cidr:
            ip_str = value[:slash_idx]
        else:
            ip_str = value

        try:
            ip_bytes = socket.inet_aton(ip_str)
        except OSError:
            # illegal IPv4 address string
            return

        if is_cidr:
            try:
                prefix_size = int(value[slash_idx+1:])
            except ValueError:
                # illegal prefix size
                return

            if prefix_size < 0 or prefix_size > 32:
                # illegal prefix size
                return

        if not is_cidr or prefix_size == 32:
            # If a CIDR with prefix size 32, drop the prefix size since it's
            # redundant.  Run the address bytes through inet_ntoa() in case it
            # would adjust the format (e.g. drop leading zeros:
            # 1.2.3.004 => 1.2.3.4).
            value = socket.inet_ntoa(ip_bytes)

        else:
            # inet_aton() gives an immutable 'bytes' value; we need a value
            # we can change.
            ip_bytes = bytearray(ip_bytes)
            _mask_bytes(ip_bytes, prefix_size)

            ip_str = socket.inet_ntoa(ip_bytes)
            value = ip_str + "/" + str(prefix_size)

        comp_expr.rhs.value = value


def ipv6_addr(comp_expr):
    """
    Canonicalizes a CIDR IPv6 address by zeroing out low-order bits, according
    to the prefix size.  This affects the rhs when the "value" property of an
    ipv6-addr is being compared.  If the prefix size is 128, the size suffix is
    simply dropped since it's redundant.  If the value is not a valid CIDR
    address, then no change is made.  This also runs the address through the
    platform's IPv6 address processing functions (inet_pton() and inet_ntop()),
    which can adjust the format.

    This side-effects the given AST.

    Args:
        comp_expr: A _ComparisonExpression object whose type is ipv6-addr.
    """
    if _path_is(comp_expr.lhs, ("value",)):
        value = comp_expr.rhs.value
        slash_idx = value.find("/")
        is_cidr = slash_idx >= 0

        if is_cidr:
            ip_str = value[:slash_idx]
        else:
            ip_str = value

        try:
            ip_bytes = socket.inet_pton(socket.AF_INET6, ip_str)
        except OSError:
            # illegal IPv6 address string
            return

        if is_cidr:
            try:
                prefix_size = int(value[slash_idx+1:])
            except ValueError:
                # illegal prefix size
                return

            if prefix_size < 0 or prefix_size > 128:
                # illegal prefix size
                return

        if not is_cidr or prefix_size == 128:
            # If a CIDR with prefix size 128, drop the prefix size since it's
            # redundant.  Run the IP address through inet_ntop() so it can
            # reformat with the double-colons (and make any other adjustments)
            # if necessary.
            value = socket.inet_ntop(socket.AF_INET6, ip_bytes)

        else:
            # inet_pton() gives an immutable 'bytes' value; we need a value
            # we can change.
            ip_bytes = bytearray(ip_bytes)
            _mask_bytes(ip_bytes, prefix_size)

            ip_str = socket.inet_ntop(socket.AF_INET6, ip_bytes)
            value = ip_str + "/" + str(prefix_size)

        comp_expr.rhs.value = value
