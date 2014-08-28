"""
The parser side of things
"""

try:
    import filters, generators, consts
except ImportError:
    from . import filters, generators, consts

from datetime import datetime
from collections import defaultdict, namedtuple
import re


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



# helper functions for
# >>> _("regexp{}", params)
# instead of
# >>> re.compile("regexp{}".format(params))
_compile_format = lambda s, *args: re.compile(s.format(*args))
_ = _compile_format


# every other Monday
add_pipe(
    _("other (?P<principle>{})", consts.re_all_day_names),
    [filters._filter_everyother, filters._filter_weekday],
    0
)

# first monday after second sunday of month
add_pipe(
    _("(?P<selector>{}) (?P<principle>{}) after (?P<selector2>{}) (?P<principle2>{}) of month", consts.re_all_selector_names, consts.re_day_names, consts.re_all_selector_names, consts.re_day_names),
    [filters._filter_identifier_in_month_after],
    0
)

# second Monday of month
add_pipe(
    _("(?P<selector>{}) (?P<principle>{}) of month", consts.re_all_selector_names, consts.re_day_names),
    [filters._filter_identifier_in_month],
    0
)

# 1st of month
add_pipe(
    re.compile("(?P<selector>[0-9]{1,2})(?:st|nd|rd|th)? of (?P<principle>month)"),
    [filters._filter_day_number_in_month],
    0
)

# end of month
add_pipe(
    re.compile("end of month"),
    [filters._filter_end_of_month],
    0
)

# friday
add_pipe(
    _("(?P<principle>{})", consts.re_all_day_names),
    [filters._filter_weekday],
    0
)

# apply time if string contains "at <time_pattern>"
add_pipe(
    _("at (?P<applicant>{})",  consts.re_all_time_names),
    [filters._apply_time],
    1
)

# cut time if string doesnt contain time pattern
add_pipe(
    _("^((?!at (?P<applicant>{})).)*$", consts.re_all_time_names),
    [filters._cut_time],
    1
)


"""Looks in the pipes list and selects a filter list and generator"""
def _find_pipes(item):
    filter_functions = []

    for priority, mapping in pipes.iteritems():
        for regexp, filters in mapping:
            result = regexp.search(item)
            if result:
                filter_functions.extend([filter_(result) for filter_ in filters])
                break

    if filter_functions:
        return consts.compose(*filter_functions), generators._generator_day

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
is at the top of the __init__.py file.
"""
def parse(timestring, start_time=None):
    if start_time is None:
        start_time = datetime.now()
    
    parts = timestring.split(" and ")
    
    generator_list = []
    for p in parts:
        filter_function, generator_function = _find_pipes(_clean(p))
        def f():
            for v in filter_function(generator_function(now=start_time)):
                yield v
        
        generator_list.append(generators.ViewableGenerator(f))
    
    the_generator = generators.SortedGenerator(lambda a,b: a > b, generator_list)
    
    for v in the_generator:
        yield v
