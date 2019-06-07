"""
Plot Helper:
This module provides plot functionalities through various Python plot packages.
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime

class PlotHelper(object):
    def plot_timeline(dates, events):
        # Choose some nice levels
        length = 20
        short_events = list(map(lambda name: name if len(name) <= length else name[0:length] + '...', events))
        levels = np.tile([-9, 9, -7, 7, -5, 5, -3, 3, -1, 1], int(np.ceil(len(dates)/10)))[:len(dates)]

        # Create figure and plot a stem plot with the date
        fig, axis = plt.subplots(figsize=(20, 4), constrained_layout=True)
        axis.set(title="Hunting Bookmarks Timeline")

        markerline, stemline, baseline = axis.stem(dates, levels,
                                                 linefmt="C1-", markerfmt="C5^", basefmt="C2-",
                                                  label="Bookmark")

        plt.setp(markerline, mec="k", mfc="w", zorder=3)

        # Shift the markers to the baseline by replacing the y-data by zeros.
        markerline.set_ydata(np.zeros(len(dates)))

        # annotate lines
        vert = np.array(['top', 'bottom'])[(levels > 0).astype(int)]
        for d, l, r, va in zip(dates, levels, short_events, vert):
            axis.annotate(r, xy=(d, l), xytext=(-3, np.sign(l)*3),
                        textcoords="offset points", va=va, ha="right")

        # format xaxis with time intervals
        axis.get_xaxis().set_major_locator(mdates.DayLocator(interval=7))
        axis.get_xaxis().set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.setp(axis.get_xticklabels(), rotation=40, ha="right")

        # remove y axis and spines
        axis.get_yaxis().set_visible(False)
        for spine in ["left", "top", "right"]: axis.spines[spine].set_visible(False)

        axis.margins(y=0.1)
        plt.show()