"""
Filters are intended to remove datetimes not meeting our criteria or to
alter datetimes (currently only to apply a time of day to a date).

The id impletmentation would be _filter_allow
"""

import calendar
import re
from functools import partial, wraps
from datetime import datetime, timedelta

try:
    import consts
except ImportError:
    from . import consts

day_indexes = dict(
    monday    = [0],
    tuesday   = [1],
    wednesday = [2],
    thursday  = [3],
    friday    = [4],
    saturday  = [5],
    sunday    = [6],
    weekday   = [0,1,2,3,4],
    weekend   = [5,6],
    day       = [0,1,2,3,4,5,6],
)

time_indexes = dict(
    noon    = (12,0),
    midday  = (12,0),
    morning = (8,0),
)


def generic_filter(filter_func):
    """Decorates filter function to value generator.

    Each function that starts with _filter should a generator, that yield value 
    based on some conditions. 

    Function like:
    
    >>> def _filter_monday(regexp_result):
    ...   monday = <process_regexp_result>
    ...   def f(gen):
    ...     for v in gen:
    ...       if v == monday:
    ...         yield v
    ...   return f

    might be defined in more generalized form:

    >>> @generic_filter
    ... def _filter_monday(regexp_result, item):
    ...   monday = <process_regexp_result>
    ...   return item == monday
    """
    @wraps(filter_func)
    def filter_(regex_result):
        def f(gen):
            for value in gen:
                if(filter_func(regex_result, value)):
                    yield value
        return f
    return filter_


@generic_filter
def _filter_allow(regex_result, value):
    pass


def _filter_everyother(regex_result):
    def f(gen):
        flag = False
        for v in gen:
            flag = not flag
            if flag:
                yield v
    return f


@generic_filter
def _filter_weekday(regex_result, value):
    the_day = regex_result.groupdict()['principle']
    acceptable_days = day_indexes[the_day]
    return value.weekday() in acceptable_days


selector_indexes = dict(
    first  = 0,
    second = 1,
    third  = 2,
    fourth = 3,
    last   = -1,
)

def _get_xs_in_month(x, year, month):
    """Used to get all Xs from a month where X is something like Tuesday"""
    day_index = day_indexes[x][0]
    c = calendar.monthcalendar(year, month)
    results = [week[day_index] for week in c if week[day_index]]

    return results


@generic_filter
def _filter_identifier_in_month(regex_result, item):
    selector = regex_result.groupdict()['selector']
    the_day = regex_result.groupdict()['principle']
    
    acceptable_days = day_indexes[the_day]
    selector_index = selector_indexes[selector]
    
    if item.weekday() in acceptable_days:
        xs_in_month = _get_xs_in_month(the_day, item.year, item.month)
        return xs_in_month[selector_index] == item.day

    return False


@generic_filter
def _filter_identifier_in_month_after(regex_result, item):
    selector = regex_result.groupdict()['selector']
    the_day = regex_result.groupdict()['principle']
    selector2 = regex_result.groupdict()['selector2']
    the_day2 = regex_result.groupdict()['principle2']    

    #calculate the 'after' date of the month
    xs_in_month = _get_xs_in_month(the_day2, item.year, item.month)
    after = datetime(item.year, item.month, xs_in_month[selector_indexes[selector2]])

    acceptable_days = day_indexes[the_day]
    selector_index = selector_indexes[selector]
    
    if item.weekday() in acceptable_days and after < item:
        xs_in_month = _get_xs_in_month(the_day, item.year, item.month)
        xs_in_month = [day for day in xs_in_month if day > after.day]  # have to skip those dates that came before the 'after' date
        return xs_in_month[selector_index] == item.day

    return False    


@generic_filter
def _filter_day_number_in_month(regex_result, item):
    selector = int(regex_result.groupdict()['selector'])
    return item.day == selector


@generic_filter
def _filter_end_of_month(regex_result, item):
    next_month = datetime(item.year, item.month, 28) + timedelta(days=4)
    last_day = next_month - timedelta(days=next_month.day)
    return item.date() == last_day.date()


"""Application functions take a value and apply changes
to it before yielding it on.
"""
_compiled_12_hour_time = re.compile(consts.re_12_hour_time.replace("?:", ""))
_compiled_12_hourmin_time = re.compile(consts.re_12_hourmin_time.replace("?:", ""))
_compiled_24_hour_time = re.compile(consts.re_24_hour_time.replace("?:", ""))
_compiled_time_names = re.compile(consts.re_time_names.replace("?:", ""))
_compiled_this_time = re.compile(consts.re_this_time)
def _apply_time(regex_result):
    def f(gen, hour, minute):
        for value in gen:
            yield datetime(value.year, value.month, value.day, hour, minute)
    
    the_time = regex_result.groupdict()['applicant']
    
    # First try it for 12 hour time
    r = _compiled_12_hour_time.match(the_time)
    if r:
        hour, suffix = r.groups()
        hour = int(hour)
        if suffix == "pm":
            hour += 12
        
        return partial(f, hour=hour, minute=0)

    # 12 hour with minutes?
    r = _compiled_12_hourmin_time.match(the_time)
    if r:
        hour, minute, suffix = r.groups()
        hour = int(hour)
        minute = int(minute)
        if suffix == "pm":
            hour += 12
        
        return partial(f, hour=hour, minute=minute)        
    
    # Okay, 24 hour time?
    r = _compiled_24_hour_time.match(the_time)
    if r:
        hour, minute = r.groups()
        hour = int(hour)
        minute = int(minute)
        return partial(f, hour=hour, minute=minute)
    
    # Named time
    r = _compiled_time_names.match(the_time)
    if r:
        hour, minute = time_indexes[r.groups()[0]]
        return partial(f, hour=hour, minute=minute)      
    
    # Relative time
    r = _compiled_this_time.match(the_time)
    if r:
        def f(gen):
            for value in gen:
                yield value
        return f

    raise Exception("Unable to find time applicant for '{}'".format(the_time))

def _cut_time(regex_result):
    def f(gen):
        for value in gen:
            yield datetime(value.year, value.month, value.day)
    return f
