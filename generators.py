"""
Generators do as the name implies, they generate a sequence of datetimes.

At the moment we've only got a single generator generating days.
"""

from datetime import datetime, timedelta

def _generator_day(now):
    d = datetime(now.year, now.month, now.day, now.hour, now.minute)
    while True:
        d = d + timedelta(days=1)
        yield d
