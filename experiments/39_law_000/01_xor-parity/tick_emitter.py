class TickEmitter:
    def __init__(self):
        self.t = 0

    def next_tick(self):
        self.t += 1
        return self.t
