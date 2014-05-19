class Bar:
    def play(self):
        pass

class Baz:
    def play(self):
        pass

def f(x):
    """
    :type x: Bar | Baz
    """

    x.playing()

