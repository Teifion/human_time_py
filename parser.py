"""
The parser side of things
"""

import filters, generators, consts
from datetime import datetime
from collections import defaultdict, namedtuple
import re


mapping = namedtuple('Mapping', 'pattern, filters')
pipes = defaultdict(lambda: [])


def add_pipe(regexp_pattern, filters, priority):
    item = mapping(regexp_pattern, filters)
    pipes[priority].append(item)


def _compile_format(s, *args):
    return re.compile(s.format(*args))

_ = _compile_format


# A matching regex
# a list of functions to compose

add_pipe(
    _("other (?P<principle>{})", consts.re_all_day_names),
    [filters._cut_time, filters._filter_everyother, filters._filter_weekday],
    0
)

add_pipe(
    _("(?P<selector>{}) (?P<principle>{}) after (?P<selector2>{}) (?P<principle2>{}) of month", consts.re_all_selector_names, consts.re_day_names, consts.re_all_selector_names, consts.re_day_names),
    [filters._cut_time, filters._filter_identifier_in_month_after],
    0
)

add_pipe(
    _("(?P<selector>{}) (?P<principle>{}) of month", consts.re_all_selector_names, consts.re_day_names),
    [filters._cut_time, filters._filter_identifier_in_month],
    0
)

add_pipe(
    re.compile("(?P<selector>[0-9]{1,2})(?:st|nd|rd|th)? of (?P<principle>month)"),
    [filters._cut_time, filters._filter_day_number_in_month],
    0
)

add_pipe(
    re.compile("end of month"),
    [filters._cut_time, filters._filter_end_of_month],
    0
)

add_pipe(
    _("(?P<principle>{})", consts.re_all_day_names),
    [filters._cut_time, filters._filter_weekday],
    0
)

add_pipe(_("at (?P<applicant>{})", consts.re_all_time_names), [filters._apply_time], 1)

"""Looks in the pipes list and selects a filter list and generator"""
def _find_pipes(item):
    rfunc = generators._generator_day
    filter_functions = []

    for priority, mapping in pipes.iteritems():
        for regexp, filters in mapping:
            result = regexp.search(item)
            if result:
                l = map(lambda f: f(result), filters)
                filter_functions.extend(l)
                break


    if filter_functions:
        filter_functions.reverse()
        return consts.compose(*filter_functions), rfunc
    """
    for regexp, filters in pipes:
        result = regexp.search(item)
        if result:

            func_list = (filter_(result) for filter_ in filters)
            return consts.compose(*func_list), rfunc
    """
    raise Exception("Unable to find pipe for item of '{}'".format(item))

"""
Clean up a string, remove double-spacing etc. Anything that might have been
mis-entered by a user.
"""
_clean_regex = re.compile(r'every')
def _clean(s):
    s = _clean_regex.sub('', s)
    
    while "  " in s:
        s = s.replace("  ", " ")
    
    return s.lower().strip()

"""
The main function. It returns the generator, a fuller readme
is at the top of the file.
"""
def parse(timestring, start_time=None):
    if start_time is None:
        start_time = datetime.now()
    
    filter_function, generator_function = _find_pipes(_clean(timestring))

    for v in filter_function(generator_function(now=start_time)):
        yield v
