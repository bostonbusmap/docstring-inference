
def f(swapper, input):
    """
    :type y: (int, str)
    :type swapper: (int, str) -> (str, int)
    :rtype: (str, int)
    """
    return swapper(*input)

def swap(x, y):
    """
    :type x: str
    :type y: int
    :rtype: (int, str)
    """

    return (y,x)

# Pylint doesn't appear to infer types within tuples
x = f(swap, (3, "4"))
print(x)

# but this should error since 'f' is not a method on Tuple
x.f()



