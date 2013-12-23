"""
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
"""

"""
The main function. It returns the generator, a fuller readme
is at the top of the file.
"""

from datetime import datetime
from .parser import parse

if __name__ == '__main__':
    import sys

    try:
        input = raw_input
    except NameError:
        pass

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
