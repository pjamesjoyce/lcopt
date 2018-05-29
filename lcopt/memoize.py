class Memoize:

    def __init__(self, fn):
        self.fn = fn
        self.memo = {}

    def __call__(self, *args):
        if str(args) not in self.memo:
            self.memo[str(args)] = self.fn(*args)
        return self.memo[str(args)]

def memoize(f):
    memo = {}
    def helper(*x):
        if str(x) not in memo:            
            memo[str(x)] = f(*x)
        return memo[str(x)]
    return helper
