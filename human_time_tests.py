import unittest
from datetime import datetime

try:
    import parser
except ImportError:
    from . import parser

class HTTester(unittest.TestCase):
    def test_parse(self):
        vals = (
            ("every tuesday", (
                datetime(2013, 12, 10),
                datetime(2013, 12, 17),
                datetime(2013, 12, 24),
            )),
            
            ("every weekday", (
                datetime(2013, 12, 5),
                datetime(2013, 12, 6),
                datetime(2013, 12, 9),
            )),
            
            ("every day", (
                datetime(2013, 12, 5),
                datetime(2013, 12, 6),
                datetime(2013, 12, 7),
            )),
            
            ("weekday at noon", (
                datetime(2013, 12, 5, 12),
                datetime(2013, 12, 6, 12),
                datetime(2013, 12, 9, 12),
            )),
            
            ("weekend at 1500", (
                datetime(2013, 12, 7, 15),
                datetime(2013, 12, 8, 15),
                datetime(2013, 12, 14, 15),
            )),
            
            ("every tuesday at 4:20am", (
                datetime(2013, 12, 10, 4, 20),
                datetime(2013, 12, 17, 4, 20),
                datetime(2013, 12, 24, 4, 20),
            )),
            
            ("every weekday at 1630", (
                datetime(2013, 12, 5, 16, 30),
                datetime(2013, 12, 6, 16, 30),
                datetime(2013, 12, 9, 16, 30),
            )),
            
            ("first monday of every month", (
                datetime(2014, 1, 6),
                datetime(2014, 2, 3),
                datetime(2014, 3, 3),
            )),
            
            ("second wednesday of every month", (
                datetime(2013, 12, 11),
                datetime(2014, 1, 8),
                datetime(2014, 2, 12),
            )),

            ("last Friday of every month at 9am", (
                datetime(2013, 12, 27, 9),
                datetime(2014, 1, 31, 9),
                datetime(2014, 2, 28, 9),
            )),
            
            ("15th of every month", (
                datetime(2013, 12, 15),
                datetime(2014, 1, 15),
                datetime(2014, 2, 15),
            )),
            
            ("21 of every month at 1430", (
                datetime(2013, 12, 21, 14, 30),
                datetime(2014, 1, 21, 14, 30),
                datetime(2014, 2, 21, 14, 30),
            )),

            ("every Monday at this time", (
                datetime(2013, 12, 9, 6, 20),
                datetime(2013, 12, 16, 6, 20),
                datetime(2013, 12, 23, 6, 20),
            )),

            ("every other Sunday at current time", (
                datetime(2013, 12, 8, 6, 20),
                datetime(2013, 12, 22, 6, 20),
            )),

            ("15th of every month at this time", (
                datetime(2013, 12, 15, 6, 20),
                datetime(2014, 1, 15, 6, 20),
                datetime(2014, 2, 15, 6, 20),
            )),

            ("end of every month", (
                datetime(2013, 12, 31),
                datetime(2014, 1, 31),
                datetime(2014, 2, 28),
            )),

            ("end of every month at 18:00", (
                datetime(2013, 12, 31, 18, 0),
                datetime(2014, 1, 31, 18, 0),
            )),
            
            ("first monday after second sunday of month", (
                datetime(2013, 12, 9),
                datetime(2014, 1, 13),
                datetime(2014, 2, 10),
                datetime(2014, 3, 10),
                datetime(2014, 4, 14),
                datetime(2014, 5, 12),
                datetime(2014, 6, 9),
                datetime(2014, 7, 14),
                datetime(2014, 8, 11),
                datetime(2014, 9, 15),
            )),

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
        start_time = datetime(
            year=2013,
            month=12,
            day=4,
            hour=6,
            minute=20,
            second=5,
        )
        
        # Display AssertionError exception 
        # with custom msg in assertEqual
        self.longMessage = True

        for str_in, expected in vals:
            gen = parser.parse(str_in, start_time=start_time)
            
            for e in expected:
                r = next(gen)
                self.assertEqual(e, r, str_in)

if __name__ == '__main__':
    unittest.main()
