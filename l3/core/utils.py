import collections
from itertools import islice


def consume(iterator, n=None):
    """Advance the iterator n-steps ahead. If n is None, consume entirely."""
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)