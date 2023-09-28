import sys
import logging

from . import markup


class AnsiMarkupFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self.ansimarkup = markup.AnsiMarkup()
        super(AnsiMarkupFormatter, self).__init__(*args)

    def format(self, record):
        message = super(AnsiMarkupFormatter, self).format(record)
        message = self.ansimarkup.parse(message)
        return message


# TODO: Add stream handler that strips tags when the output stream is not a tty.
