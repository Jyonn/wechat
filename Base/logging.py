class Logging:
    def __init__(self, log_file):
        self._log_file = log_file

    def __call__(self, line):
        with open(self._log_file, 'a') as f:
            f.write(line + '\n')
