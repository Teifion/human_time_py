import re
import filters, generators, consts
from datetime import datetime
from collections import defaultdict, namedtuple
from consts import DatePattern, TimePattern

mapping = namedtuple('Mapping', 'pattern, filters')
pipes = defaultdict(lambda: [])

def add_pipe(regex, filters, priority):
    """Registers new pipe.

    Register new pipe in internal structure.

    @param regex: regular expression that will trigger filters
    @param filters: collection of filter generators
    @param priority: used to sort execution order of filters
    """
    item = mapping(regex, filters)
    pipes[priority].append(item)


default_pipes = (
    (
        (
            # every other Monday
            r"other (?P<principle>%(ALL_DAY_NAMES)s)" % vars(DatePattern),
            [filters._filter_everyother, filters._filter_weekday]
        ),
        (
            # first monday after second sunday of month
            r"(?P<selector>%(SELECTOR_NAMES)s) (?P<principle>%(DAY_NAMES)s) after (?P<selector2>%(SELECTOR_NAMES)s) (?P<principle2>%(DAY_NAMES)s) of month" % vars(DatePattern),
            [filters._filter_identifier_in_month_after]
        ),
        (
            # first monday of month
            r"(?P<selector>%(SELECTOR_NAMES)s) (?P<principle>%(DAY_NAMES)s) of month" % vars(DatePattern),
            [filters._filter_identifier_in_month],
        ),
        (
            # 1st of month
            r"(?P<selector>[0-9]{1,2})(?:st|nd|rd|th)? of (?P<principle>month)",
            [filters._filter_day_number_in_month],
        ),
        (
            # end of month
            r"end of month",
            [filters._filter_end_of_month],
        ),
        (
            # friday
            r"(?P<principle>%(ALL_DAY_NAMES)s)" % vars(DatePattern),
            [filters._filter_weekday],
        )
    ),
    (
        (
            r"at (?P<applicant>%(TIME_ALL)s)" % vars(TimePattern),
            [filters._apply_time]
        ),
        (
            r"^((?!at (?P<applicant>%(TIME_ALL)s)).)*$" % vars(TimePattern),
            [filters._cut_time]
        )
    )
)

# register default groups
for priority, group in enumerate(default_pipes):
    for regexp, filters in group:
        add_pipe(re.compile(regexp), filters, priority)


def _find_pipes(item):
    """Looks in the pipes list and selects a filter list"""

    filter_functions = []

    for priority, mapping in pipes.iteritems():
        for regexp, filters in mapping:
            result = regexp.search(item)
            if result:
                filter_functions.extend([filter_(result) for filter_ in filters])
                break

    if filter_functions:
        return filter_functions

    raise Exception("Unable to find pipe for item of '{}'".format(item))


_clean_regex = re.compile(r'every')
def _clean(s):
    """ Clean up a string, remove double-spacing etc. """
    s = _clean_regex.sub('', s)

    while "  " in s:
        s = s.replace("  ", " ")
    
    return s.lower().strip()

def parse(timestring, start_time=None, gen_func=None):
    """Returns datetime generator with applied filters

    @param timestring: human time expression
    @param start_time: initial time
    @param gen_func: tbd
    """

    if start_time is None:
        start_time = datetime.now()

    if gen_func is None:
        gen_func = generators._generator_day

    filter_functions = _find_pipes(_clean(timestring))
    chained = consts.compose(filter_functions)

    for v in chained(gen_func(now=start_time)):
        yield v
