def f(x, y):
    """
    :type y: list[int]
    :type x: str
    :rtype: int
"""
    y.append(int(x))
    try:
        # this should error since list has no 'x' member
        y.x()
    except:
        pass
    return int(x)

print(f("4", [1,2,3]))
