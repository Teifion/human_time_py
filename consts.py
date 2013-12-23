"""
A set of strings used to build certain regular expressions. Additionally
we define our function composition function here.

We build up the patterns later and only save them as strings here because
this allows us more flexibility in using them later.
"""

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
re_12_hour_time = r"(?:[0-9]|1[0-2])(?:am|pm)"# 4pm
re_12_hourmin_time = r"(?:[0-9]|1[0-2]):(?:[0-5][0-9])(?:am|pm)"# 4:30pm
re_24_hour_time = r"(?:[01]?[0-9]|2[0-3]):?(?:[0-5][0-9])"# 1630, 16:30
re_time_names = r"(?:noon|midday|morning)"
re_this_time = r"(?:(this|current) time)"
re_all_time_names = r"(?:{}|{}|{}|{}|{})".format(re_12_hour_time, re_12_hourmin_time, re_24_hour_time, re_time_names, re_this_time)


"""
Allows us to compose functions
For those familiar with Haskell it's the same as the dot operator
"""
idfunc = lambda x: x
def compose(f1=idfunc, f2=idfunc, *more_funcs):
    # Allows us an unlimited number of functions
    if len(more_funcs) > 0:
        f2 = compose(f2, *more_funcs)
    
    # The magic happens here
    def new_f(*args, **kwards):
        return f1(f2(*args, **kwards))
    return new_f