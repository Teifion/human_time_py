"""
Filters are intended to remove datetimes not meeting our criteria or to
alter datetimes (currently only to apply a time of day to a date).

The id impletmentation would be _filter_allow
"""

import calendar
import re
from datetime import datetime, timedelta
import consts

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

def _filter_allow(regex_result):
    def f(gen):
        for v in gen:
            yield v
    return f

def _filter_everyother(regex_result):
    def f(gen):
        flag = False
        for v in gen:
            flag = not flag
            if flag:
                yield v
    return f

def _filter_weekday(regex_result):
    the_day = regex_result.groupdict()['principle']
    acceptable_days = day_indexes[the_day]
    
    def f(gen):
        for v in gen:
            if v.weekday() in acceptable_days:
                yield v
    return f

selector_indexes = dict(
    first  = 0,
    second = 1,
    third  = 2,
    fourth = 3,
    last   = -1,
)

def _get_xs_in_month(x, year, month):
    """Used to get all Xs from a month where X is something like Tuesday"""
    x_index = day_indexes[x][0]
    
    c = calendar.monthcalendar(year, month)
    
    results = []
    for week in c:
        if week[x_index] > 0:
            results.append(week[x_index])
    
    return results

def _filter_identifier_in_month(regex_result):
    selector = regex_result.groupdict()['selector']
    the_day = regex_result.groupdict()['principle']
    
    acceptable_days = day_indexes[the_day]
    selector_index = selector_indexes[selector]
    
    def f(gen):
        for v in gen:
            # Is it an acceptable day?
            if v.weekday() not in acceptable_days:
                continue
            
            # We know it's the right day, is it the right instance of this month?
            xs_in_month = _get_xs_in_month(the_day, v.year, v.month)
            if xs_in_month[selector_index] == v.day:
                yield v
            
    return f

def _filter_day_number_in_month(regex_result):
    selector = int(regex_result.groupdict()['selector'])
    
    def f(gen):
        for v in gen:
            if v.day == selector:
                yield v
    
    return f

"""Application functions take a value and apply changes
to it before yielding it on.
"""
_compiled_12_hour_time = re.compile(consts.re_12_hour_time.replace("?:", ""))
_compiled_12_hourmin_time = re.compile(consts.re_12_hourmin_time.replace("?:", ""))
_compiled_24_hour_time = re.compile(consts.re_24_hour_time.replace("?:", ""))
_compiled_time_names = re.compile(consts.re_time_names.replace("?:", ""))
_compiled_this_time = re.compile(consts.re_this_time)
def _apply_time(regex_result):
    the_time = regex_result.groupdict()['applicant']
    
    # First try it for 12 hour time
    r = _compiled_12_hour_time.match(the_time)
    if r:
        hour, suffix = r.groups()
        hour = int(hour)
        if suffix == "pm":
            hour += 12
        
        def f(gen):
            for v in gen:
                yield datetime(v.year, v.month, v.day, hour)
        return f
    
    # 12 hour with minutes?
    r = _compiled_12_hourmin_time.match(the_time)
    if r:
        hour, minute, suffix = r.groups()
        hour = int(hour)
        minute = int(minute)
        if suffix == "pm":
            hour += 12
        
        def f(gen):
            for v in gen:
                yield datetime(v.year, v.month, v.day, hour, minute)
        return f
    
    # Okay, 24 hour time?
    r = _compiled_24_hour_time.match(the_time)
    if r:
        hour, minute = r.groups()
        hour = int(hour)
        minute = int(minute)
        def f(gen):
            for v in gen:
                yield datetime(v.year, v.month, v.day, hour, minute)
        return f
    
    # Named time
    r = _compiled_time_names.match(the_time)
    if r:
        hour, minute = time_indexes[r.groups()[0]]
        
        def f(gen):
            for v in gen:
                yield datetime(v.year, v.month, v.day, hour, minute)
        return f
    
    # Relative time
    r = _compiled_this_time.match(the_time)
    if r:
        def f(gen):
            for v in gen:
                yield v
        return f

    raise Exception("Unable to find time applicant for '{}'".format(the_time))

def _cut_time(regex_result):
    def f(gen):
        for v in gen:
            yield datetime(v.year, v.month, v.day)
    return f

def _end_of_month(regex_result):
    def f(gen):
        for v in gen:
            next_month = datetime(v.year, v.month, 28) + timedelta(days=4) 
            last_day = next_month - timedelta(days=next_month.day)
            if v.date() == last_day.date():
                yield v
    return f
