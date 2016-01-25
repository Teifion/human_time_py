"""
Filters are intended to remove datetimes not meeting our criteria or to
alter datetimes (currently only to apply a time of day to a date).
"""

import re
import calendar
import consts
from functools import partial, wraps
from datetime import datetime, timedelta
from consts import DAY_INDEXES, TIME_INDEXES, SELECTOR_INDEXES
from consts import TimePattern

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
            for v in gen:
                if filter_func(regex_result, v):
                    yield v
        return f

    return filter_

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
    return item.weekday() in DAY_INDEXES[the_day]

def _get_xs_in_month(x, year, month):
    """Used to get all Xs from a month where X is something like Tuesday"""
    day_index = DAY_INDEXES[x][0]
    c = calendar.monthcalendar(year, month)
    results = [week[day_index] for week in c if week[day_index]]

    return results


@generic_filter
def _filter_identifier_in_month(regex_result, item):
    selector = regex_result.groupdict()['selector']
    the_day = regex_result.groupdict()['principle']
    
    acceptable_days = DAY_INDEXES[the_day]
    selector_index = SELECTOR_INDEXES[selector]
    
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
    after = datetime(item.year, item.month, xs_in_month[SELECTOR_INDEXES[selector2]])

    acceptable_days = DAY_INDEXES[the_day]
    selector_index = SELECTOR_INDEXES[selector]
    
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
#_compiled_12_hour_time = re.compile(Pattern.TIME_12H)
_compiled_12_hourmin_time = re.compile(TimePattern.TIME_12H)
_compiled_24_hour_time = re.compile(TimePattern.TIME_24H)
_compiled_time_names = re.compile(TimePattern.TIME_TERM)
_compiled_this_time = re.compile(TimePattern.TIME_CURRENT)

def _apply_time(regex_result):
    def f(gen, hour, minute):
        for value in gen:
            yield datetime(value.year, value.month, value.day, hour, minute)
    
    the_time = regex_result.groupdict()['applicant']

    r = _compiled_12_hourmin_time.match(the_time)
    if r:
        groupdict = r.groupdict()
        hour = int(groupdict.get("hour") or 0)
        minute = int(groupdict.get("minute") or 0)
        suffix = groupdict.get("suffix")
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
        hour, minute = TIME_INDEXES[r.groups()[0]]
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
