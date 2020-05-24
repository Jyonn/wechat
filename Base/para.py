class Para:
    def __init__(self, *lines: str):
        self.lines = '\n'.join(lines)

    def __str__(self):
        return self.lines
