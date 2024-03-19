import timeit


class Timer(object):
    def __init__(self, task='action', verbose=True, level=0):
        self.task = task
        self.verbose = verbose
        self.timer = timeit.default_timer
        self.level = level

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        end = self.timer()
        self.elapsed_secs = end - self.start
        self.elapsed = self.elapsed_secs * 1000  # milliseconds
        if self.verbose:
            print('\t' * self.level + '%s took:\t% 7d ms' % (self.task, self.elapsed))
