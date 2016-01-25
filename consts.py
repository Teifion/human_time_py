"""
A set of strings used to build certain regular expressions. Additionally
we define our function composition function here.

We build up the patterns later and only save them as strings here because
this allows us more flexibility in using them later.
"""

class DatePattern:
    """Namespace for date related regular expressions"""

    SELECTOR_NAMES = "first|1st|second|2nd|third|3rd|fourth|4th|last"
    DAY_NAMES = "monday|tuesday|wednesday|thursday|friday|saturday|sunday"
    ALL_DAY_NAMES = DAY_NAMES + "|weekday|day"
    MONTH_NAMES = "january|february|march|april|may|june|july|august|september|october|november|december"

class TimePattern:
    """Namespace for time regular expressions"""

    TIME_TERM = r"(noon|midday|morning)"
    TIME_CURRENT = r"(this|current) time"
    TIME_12H = r"(?P<hour>[0-9]|1[0-2])(:(?P<minute>[0-5][0-9]))?(?P<period>am|pm)"
    TIME_24H = r"([01]?[0-9]|2[0-3]):?([0-5][0-9])"
    TIME_ALL = r"(?:{}|{}|{}|{})".format(TIME_12H, TIME_24H, TIME_TERM, TIME_CURRENT)


DAY_INDEXES = dict(
    monday    = [0],
    tuesday   = [1],
    wednesday = [2],
    thursday  = [3],
    friday    = [4],
    saturday  = [5],
    sunday    = [6],
    weekday   = [0, 1, 2, 3, 4],
    weekend   = [5, 6],
    day       = [0, 1, 2, 3, 4, 5, 6],
)


TIME_INDEXES = dict(
    noon    = (12, 0),
    midday  = (12, 0),
    morning = (8, 0),
)


SELECTOR_INDEXES = dict(
    first  = 0,
    second = 1,
    third  = 2,
    fourth = 3,
    last   = -1,
)


def compose(functions):
    def chained(value):
        result = None
        while functions:
            try:
                func = functions.pop()
                result = func(result or value)
            except IndexError:
                break
        return result

    return chained
