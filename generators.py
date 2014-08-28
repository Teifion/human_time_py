"""
Generators do as the name implies, they generate a sequence of datetimes.

At the moment we've only got a single generator generating days.
"""

from datetime import datetime, timedelta

def _generator_day(now):
    d = datetime(now.year, now.month, now.day, now.hour, now.minute)
    while True:
        d = d + timedelta(days=1)
        yield d

class ViewableGenerator(object):
    """Allows us to test the next value before actually popping it"""
    def __init__(self, the_generator):
        super(ViewableGenerator, self).__init__()
        self.g = the_generator()
        self.v = next(self.g)
    
    def view(self):
        return self.v
    
    def pop(self):
        return_value = self.v
        self.v = next(self.g)
        return return_value

class SortedGenerator(object):
    """Takes multiple ViewableGenerators, a sorting function and combines them
    
    The sort_function should return False if we want the first value, True if we want the second
    This way we can use "if sort_function(a,b): use b"
    """
    
    def __init__(self, sort_function, generators):
        super(SortedGenerator, self).__init__()
        
        self.sort_function = sort_function
        self.generators = generators
    
    def __iter__(self):
        return self
    
    def __next__(self):
        return self.next()
    
    def next(self):
        selected_generator = 0
        selected_value = self.generators[0].view()
        
        for i in range(len(self.generators)-1):
            g = self.generators[i+1]
            temp_value = g.view()
            
            if self.sort_function(selected_value, temp_value):
                selected_value = temp_value
                selected_generator = i+1
        
        return self.generators[selected_generator].pop()
