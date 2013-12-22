Human time
==========
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


Outline of how it does it
=========================

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


Written by Tefion Jordan
