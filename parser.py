"""
The parser side of things
"""

# I can't work out why but I'm currently getting errors
# about it being a non-package and thus not able to use
# relative imports
try:
    from . import filters, generators, consts
except ValueError:
    import filters, generators, consts

from datetime import datetime
import re

# A matching regex
# a list of functions to compose
# a generator
pipes = (
    # Days
    (re.compile(r"^(?P<principle>{})$".format(consts.re_all_day_names)),
        [filters._cut_time, filters._filter_weekday],
        generators._generator_day,
    ),
    
    # We are looking for a day name (e.g. tusday) with a time after it (e.g. 8pm)
    # we have some regex patterns already defined up the top
    # our filter/map pipeline will ensure it's a weekday of the type found and apply the time
    # these two functions use the named regex groups to pull the correct part from the text
    # finally we know we are dealing with entire days so we generate on a day by day basis
    (re.compile(r"^(?P<principle>{}) at (?P<applicant>{})$".format(consts.re_all_day_names, consts.re_all_time_names)),
        [filters._apply_time, filters._filter_weekday],
        generators._generator_day,
    ),

    (re.compile(r"^other (?P<principle>{}) at (?P<applicant>{})$".format(consts.re_all_day_names, consts.re_all_time_names)),
        [filters._apply_time, filters._filter_everyother, filters._filter_weekday],
        generators._generator_day,
    ),

    
    (re.compile(r"^other (?P<principle>{})$".format(consts.re_all_day_names)),
        [filters._cut_time, filters._filter_everyother, filters._filter_weekday],
        generators._generator_day,
    ),
    
    # Months
    (re.compile(r"^(?P<selector>{}) (?P<principle>{}) of every month$".format(consts.re_all_selector_names, consts.re_day_names)),
        [filters._cut_time, filters._filter_identifier_in_month],
        generators._generator_day,
    ),
    
    (re.compile(r"^(?P<selector>[0-9]{1,2})(?:st|nd|rd|th)? of every (?P<principle>month)$"),
        [filters._cut_time, filters._filter_day_number_in_month],
        generators._generator_day,
    ),
    
    (re.compile(r"^(?P<selector>[0-9]{1,2})(?:st|nd|rd|th)? of every (?P<principle>month) at (?P<applicant>%s)$" % (consts.re_all_time_names)),
        [filters._apply_time, filters._filter_day_number_in_month],
        generators._generator_day,
    ),
    
    (re.compile(r"^(?P<selector>{}) (?P<principle>{}) of every month at (?P<applicant>{})$".format(consts.re_all_selector_names, consts.re_day_names, consts.re_all_time_names)),
        [filters._apply_time, filters._filter_identifier_in_month],
        generators._generator_day,
    ),
    
    # Default implementation
    (re.compile(r"^(?P<principle>{})$".format(consts.re_time_periods)),
        [],
        generators._generator_day
    ),
)

"""Looks in the pipes list and selects a filter list and generator"""
def _find_pipes(item):
    for preg, ps, rfunc in pipes:
        result = preg.search(item)
        if result:
            func_list = (p(result) for p in ps)
            return consts.compose(*func_list), rfunc
    
    raise Exception("Unable to find pipe for item of '{}'".format(item))

"""
Clean up a string, remove double-spacing etc. Anything that might have been
mis-entered by a user.
"""
_clean_regex = re.compile(r'^every ?')
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
