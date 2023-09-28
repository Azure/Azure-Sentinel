"""
Validates a user entered pattern against STIXPattern grammar.
"""

from __future__ import print_function

import argparse

from antlr4 import InputStream
import six

from . import DEFAULT_VERSION
from .exceptions import STIXPatternErrorListener  # noqa: F401
from .helpers import brackets_check
from .v20.validator import run_validator as run_validator20
from .v21.validator import run_validator as run_validator21


def run_validator(pattern, stix_version=DEFAULT_VERSION):
    """
    Validates a pattern against the STIX Pattern grammar.  Error messages are
    returned in a list.  The test passed if the returned list is empty.
    """
    if isinstance(pattern, six.string_types):
        pattern_str = pattern
        pattern = InputStream(pattern)

    else:
        pattern_str = pattern.readline()
        pattern.seek(0)

    if stix_version == '2.1':
        err_messages = run_validator21(pattern)
    else:
        err_messages = run_validator20(pattern)

    if not brackets_check(pattern_str):
        err_messages.insert(
            0,
            "FAIL: Error found at line 1:0. input is missing square brackets"
        )

    return err_messages


def validate(user_input, stix_version=DEFAULT_VERSION, ret_errs=False, print_errs=False):
    """
    Wrapper for run_validator function that returns True if the user_input
    contains a valid STIX pattern or False otherwise. The error messages may
    also be returned or printed based upon the ret_errs and print_errs arg
    values.
    """

    errs = run_validator(user_input, stix_version)
    passed = len(errs) == 0

    if print_errs:
        for err in errs:
            print(err)

    if ret_errs:
        return passed, errs

    return passed


def main():
    """
    Continues to validate patterns until it encounters EOF within a pattern
    file or Ctrl-C is pressed by the user.
    """
    parser = argparse.ArgumentParser(description='Validate STIX Patterns.')
    parser.add_argument('-f', '--file',
                        help="Specify this arg to read patterns from a file.",
                        type=argparse.FileType("r"))
    parser.add_argument('-v', '--version',
                        default=DEFAULT_VERSION,
                        help="Specify version of STIX 2 specification to validate against.")
    args = parser.parse_args()

    pass_count = fail_count = 0

    # I tried using a generator (where each iteration would run raw_input()),
    # but raw_input()'s behavior seems to change when called from within a
    # generator: I only get one line, then the generator completes!  I don't
    # know why behavior changes...
    import functools
    if args.file:
        nextpattern = args.file.readline
    else:
        nextpattern = functools.partial(six.moves.input, "Enter a pattern to validate: ")

    try:
        while True:
            pattern = nextpattern()
            if not pattern:
                break
            tests_passed, err_strings = validate(pattern, args.version, True)

            if tests_passed:
                print("\nPASS: %s" % pattern)
                pass_count += 1

            else:
                for err in err_strings:
                    print(err, '\n')
                fail_count += 1
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        if args.file:
            args.file.close()

    print("\nPASSED:", pass_count, " patterns")
    print("FAILED:", fail_count, " patterns")


if __name__ == '__main__':
    main()
