"""
Written by Tefion Jordan

The purpose of this library is to take human written time such as "every other tuesday", "every weekday",
"every friday at 2pm" etc, and convert it into a sequence of datetimes meeting the required parameters.
The sequence is represented as a generator without a temination so it must be treated as an infinite list.

Main functions is parse(), it returns a generator supplying the sequence

  Some example strings:
Tuesday
Every other wednesday
Weekday
First friday of every month
Last weekday of every month
Thursday at 1200
Weekday at 09:30
Saturday at 4pm
Saturday at 4:30pm
Sunday at noon
Last friday of every month at 8am
16th of every month
4th of every month at 4pm

You can test this module by running it with the string after the file name (you can use spaces)
or without any arguments in which case it will prompt you for an input.


  Readme for developers/maintainers/people that want to use the code

parse() cleans up the input searches through the pipes for a valid handler
once a handler is found we are given a base generator and a set of filter functions

You end up with a pipeline of the following:

f1 . f2 . fx . g

or

f1(f2(fx(g)))

Where f is a filter/applier function and g is the generator. Filters will discard any values
not meeting their criteria while appliers will alter values passing through them. In principle
the signature for each is identical, the only difference lies in their use/purpose.

-- To add a new handler --
Add a new entry to pipes, one of the first entries has extra comments to help.

-- Todo --
I'm pretty sure the pipes regex search could be improved if it were an actual parser.
Add support for relative times such as "this time every week"
"""

import calendar
import re
from datetime import datetime, timedelta

re_all_selector_names = "first|1st|second|2nd|third|3rd|fourth|4th|last"

re_day_names = "monday|tuesday|wednesday|thursday|friday|saturday|sunday"
day_names = re_day_names.split("|")

re_all_day_names = re_day_names + "|weekday|day"
all_day_names = re_all_day_names.split("|")

re_month_names = "january|february|march|april|may|june|july|august|september|october|november|december"
month_names = re_month_names.split("|")

re_time_periods = "day|weekday|weekend|month|{}|{}".format(re_day_names, re_month_names)
time_periods = re_time_periods.split("|")

"""You can define hours:mins in many ways"""
re_12_hour_time = r"(?:[0-9]|1[0-2])(?:am|pm)?"# 4pm
re_12_hourmin_time = r"(?:[0-9]|1[0-2]):(?:[0-5][0-9])(?:am|pm)?"# 4:30pm
re_24_hour_time = r"(?:[01]?[0-9]|2[0-3]):?(?:[0-5][0-9])"# 1630, 16:30
re_time_names = r"(?:noon|midday|morning)"
re_all_time_names = r"(?:{}|{}|{}|{})".format(re_12_hourmin_time, re_12_hour_time, re_24_hour_time, re_time_names)

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

"""Allows us to compose functions"""
idfunc = lambda x: x
def compose(f1=idfunc, f2=idfunc, *more_funcs):
    # Allows us an unlimited number of functions
    if len(more_funcs) > 0:
        f2 = compose(f2, *more_funcs)
    
    # The magic happens here
    def new_f(*args, **kwards):
        return f1(f2(*args, **kwards))
    return new_f

"""Generators create a sequence of datetimes with a regular interval"""
def _generator_day(now):
    d = datetime(now.year, now.month, now.day)
    while True:
        d = d + timedelta(days=1)
        yield d


"""All filter functions return a new generator. They take the regex result to
build such a filter
The id impletmentation would be _filter_allow"""
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
_compiled_12_hour_time = re.compile(re_12_hour_time.replace("?:", ""))
_compiled_12_hourmin_time = re.compile(re_12_hourmin_time.replace("?:", ""))
_compiled_24_hour_time = re.compile(re_24_hour_time.replace("?:", ""))
_comiled_time_names = re.compile(re_time_names.replace("?:", ""))
def _apply_time(regex_result):
    the_time = regex_result.groupdict()['applicant']
    
    # 24 hour time?
    r = _compiled_24_hour_time.match(the_time)
    if r:
        hour, minute = r.groups()
        hour = int(hour)
        minute = int(minute)
        def f(gen):
            for v in gen:
                yield datetime(v.year, v.month, v.day, hour, minute)
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
    
    # 12 hour time without minutes
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
    
    
    
    # Named time
    r = _comiled_time_names.match(the_time)
    if r:
        hour, minute = time_indexes[r.groups()[0]]
        
        def f(gen):
            for v in gen:
                yield datetime(v.year, v.month, v.day, hour, minute)
        return f
    
    raise Exception("Unable to find time applicant for '{}'".format(the_time))

# A matching regex
# a list of functions to compose
# a generator
pipes = (
    # Days
    (re.compile(r"^(?P<principle>{})$".format(re_all_day_names)),
        [_filter_weekday],
        _generator_day,
    ),
    
    # We are looking for a day name (e.g. tuesday) with a time after it (e.g. 8pm)
    # we have some regex patterns already defined up the top
    # our filter/map pipeline will ensure it's a weekday of the type found and apply the time
    # these two functions use the named regex groups to pull the correct part from the text
    # finally we know we are dealing with entire days so we generate on a day by day basis
    (re.compile(r"^(?P<principle>{}) at (?P<applicant>{})$".format(re_all_day_names, re_all_time_names)),
        [_apply_time, _filter_weekday],
        _generator_day,
    ),
    
    (re.compile(r"^other (?P<principle>{})$".format(re_all_day_names)),
        [_filter_everyother, _filter_weekday],
        _generator_day,
    ),
    
    # Months
    (re.compile(r"^(?P<selector>{}) (?P<principle>{}) of every month$".format(re_all_selector_names, re_day_names)),
        [_filter_identifier_in_month],
        _generator_day,
    ),
    
    (re.compile(r"^(?P<selector>[0-9]{1,2})(?:st|nd|rd|th)? of every (?P<principle>month)$"),
        [_filter_day_number_in_month],
        _generator_day,
    ),
    
    (re.compile(r"^(?P<selector>[0-9]{1,2})(?:st|nd|rd|th)? of every (?P<principle>month) at (?P<applicant>%s)$" % (re_all_time_names)),
        [_apply_time, _filter_day_number_in_month],
        _generator_day,
    ),
    
    (re.compile(r"^(?P<selector>{}) (?P<principle>{}) of every month at (?P<applicant>{})$".format(re_all_selector_names, re_day_names, re_all_time_names)),
        [_apply_time, _filter_identifier_in_month],
        _generator_day,
    ),
    
    # Default implementation
    (re.compile(r"^(?P<principle>{})$".format(re_time_periods)),
        [],
        _generator_day,
    ),
)

"""Looks in the pipes list and selects a filter list and generator"""
def _find_pipes(item):
    for preg, ps, rfunc in pipes:
        result = preg.search(item)
        if result:
            func_list = (p(result) for p in ps)
            return compose(*func_list), rfunc
    
    raise Exception("Unable to find pipe for item of '{}'".format(item))

"""
Clean up a string, remove double-spacing etc. Anything that might have been
mis-entered by a user.
"""
_clean_regex = re.compile(r'^every ?')
def _clean(s):
    s = _clean_regex.sub('', s.lower().strip())
    
    while "  " in s:
        s = s.replace("  ", " ")
    
    return s.strip()

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

def parse_amount(timestring, start_time=None, amount=1):
    gen = parse(timestring, start_time)
    return [next(gen) for i in range(amount)]

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        time_string = " ".join(sys.argv[1:])
    else:
        time_string = input("Please enter the timestring you wish to parse (e.g. every other tuesday): ")
    
    start_time = datetime(
        year = 2013,
        month = 12,
        day = 4,
        hour = 6,
        minute = 20,
        second = 5,
    )
    
    """
    A calendar of December 2013 (the month this date falls into)
    for your reference.
    
       December 2013
    Su Mo Tu We Th Fr Sa
     1  2  3  4  5  6  7
     8  9 10 11 12 13 14
    15 16 17 18 19 20 21
    22 23 24 25 26 27 28
    29 30 31
    """
    
    print("")
    print(time_string)
    g = parse(time_string)
    for i in range(5):
        print(next(g))
    print("")