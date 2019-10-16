import time
from functools import wraps

def timethis(func):
    '''
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end-start)
        return result
    return wrapper

@timethis
def countdown(n):
    '''
    Counts down
    '''
    while n > 0:
        n -= 1


def parse_int(s):
    try:
        n = int(v)
    except Exception as e:
        print("Couldn't parse")
        print('Reason:',e)

def example():
    try:
        int('N/A')
    except ValueError as e:
        raise RuntimeError('A parsing error occured') from e
                           
